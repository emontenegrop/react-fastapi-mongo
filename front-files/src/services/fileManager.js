// src/services/fileManager.js
import { fileService } from './api';

export class FileManager {
  constructor() {
    this.uploadQueue = [];
    this.uploadProgress = new Map();
    this.maxConcurrentUploads = 3;
    this.activeUploads = 0;
  }

  // File validation
  validateFile(file, options = {}) {
    const {
      maxSize = 10 * 1024 * 1024, // 10MB default
      allowedTypes = [
        'image/jpeg',
        'image/png',
        'image/gif',
        'application/pdf',
        'text/plain'
      ],
      maxFiles = 10
    } = options;

    const errors = [];

    // Check file size
    if (file.size > maxSize) {
      errors.push(`File size exceeds ${this.formatFileSize(maxSize)}`);
    }

    // Check file type
    if (!allowedTypes.includes(file.type)) {
      errors.push(`File type ${file.type} is not allowed`);
    }

    // Check file name for security
    if (this.hasUnsafeFileName(file.name)) {
      errors.push('File name contains unsafe characters');
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  // Check for unsafe file names
  hasUnsafeFileName(fileName) {
    const unsafePatterns = [
      /\.\./,           // Path traversal
      /[<>:"|?*]/,      // Windows forbidden characters
      /^\./,            // Hidden files (starting with dot)
      /\.(exe|bat|cmd|scr|vbs|js)$/i // Executable files
    ];

    return unsafePatterns.some(pattern => pattern.test(fileName));
  }

  // Format file size for display
  formatFileSize(bytes) {
    const units = ['B', 'KB', 'MB', 'GB'];
    let size = bytes;
    let unitIndex = 0;

    while (size >= 1024 && unitIndex < units.length - 1) {
      size /= 1024;
      unitIndex++;
    }

    return `${size.toFixed(1)} ${units[unitIndex]}`;
  }

  // Get file type category
  getFileCategory(mimeType) {
    if (mimeType.startsWith('image/')) return 'image';
    if (mimeType.startsWith('video/')) return 'video';
    if (mimeType.startsWith('audio/')) return 'audio';
    if (mimeType.includes('pdf')) return 'document';
    if (mimeType.includes('text/') || mimeType.includes('document')) return 'document';
    if (mimeType.includes('spreadsheet') || mimeType.includes('excel')) return 'spreadsheet';
    if (mimeType.includes('presentation') || mimeType.includes('powerpoint')) return 'presentation';
    if (mimeType.includes('zip') || mimeType.includes('rar') || mimeType.includes('tar')) return 'archive';
    return 'other';
  }

  // Upload single file
  async uploadFile(file, options = {}) {
    const {
      onProgress,
      metadata = {},
      validateFirst = true
    } = options;

    // Validate file if requested
    if (validateFirst) {
      const validation = this.validateFile(file);
      if (!validation.isValid) {
        throw new Error(`File validation failed: ${validation.errors.join(', ')}`);
      }
    }

    // Create upload progress tracker
    const uploadId = Date.now().toString() + Math.random().toString(36).substr(2, 9);
    
    this.uploadProgress.set(uploadId, {
      fileName: file.name,
      fileSize: file.size,
      progress: 0,
      status: 'uploading',
      startTime: Date.now()
    });

    try {
      const enrichedMetadata = {
        ...metadata,
        fileName: file.name,
        fileSize: file.size,
        fileType: file.type,
        category: this.getFileCategory(file.type),
        uploadId,
        onUploadProgress: (progressEvent) => {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          
          this.uploadProgress.set(uploadId, {
            ...this.uploadProgress.get(uploadId),
            progress,
            loaded: progressEvent.loaded,
            total: progressEvent.total
          });

          if (onProgress) {
            onProgress({
              ...progressEvent,
              progress,
              uploadId,
              fileName: file.name
            });
          }
        }
      };

      const result = await fileService.uploadFile(file, enrichedMetadata);

      this.uploadProgress.set(uploadId, {
        ...this.uploadProgress.get(uploadId),
        status: 'completed',
        result
      });

      return {
        ...result,
        uploadId
      };

    } catch (error) {
      this.uploadProgress.set(uploadId, {
        ...this.uploadProgress.get(uploadId),
        status: 'error',
        error: error.message
      });

      throw error;
    }
  }

  // Upload multiple files with queue management
  async uploadFiles(files, options = {}) {
    const {
      onProgress,
      onFileComplete,
      onAllComplete,
      validateFirst = true
    } = options;

    const uploads = [];
    const results = [];
    const errors = [];

    // Validate all files first if requested
    if (validateFirst) {
      for (const file of files) {
        const validation = this.validateFile(file);
        if (!validation.isValid) {
          errors.push({
            fileName: file.name,
            errors: validation.errors
          });
        }
      }

      if (errors.length > 0) {
        throw new Error(`File validation failed for ${errors.length} files`);
      }
    }

    // Create upload promises
    for (const file of files) {
      const uploadPromise = this.uploadFile(file, {
        ...options,
        validateFirst: false, // Already validated above
        onProgress: (progress) => {
          if (onProgress) {
            onProgress(progress);
          }
        }
      }).then(result => {
        results.push(result);
        if (onFileComplete) {
          onFileComplete(result);
        }
        return result;
      }).catch(error => {
        errors.push({
          fileName: file.name,
          error: error.message
        });
        throw error;
      });

      uploads.push(uploadPromise);
    }

    try {
      // Wait for all uploads to complete
      await Promise.allSettled(uploads);
      
      if (onAllComplete) {
        onAllComplete({ results, errors });
      }

      return { results, errors };
    } catch (error) {
      throw error;
    }
  }

  // Download file with progress
  async downloadFile(fileId, fileName, options = {}) {
    const { onProgress } = options;

    try {
      const response = await fileService.downloadFile(fileId);
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response]));
      const link = document.createElement('a');
      link.href = url;
      link.download = fileName || `file-${fileId}`;
      
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      // Clean up
      window.URL.revokeObjectURL(url);

      if (onProgress) {
        onProgress({ status: 'completed' });
      }

      return true;
    } catch (error) {
      if (onProgress) {
        onProgress({ status: 'error', error: error.message });
      }
      throw error;
    }
  }

  // Get upload progress for a specific upload
  getUploadProgress(uploadId) {
    return this.uploadProgress.get(uploadId);
  }

  // Get all upload progress
  getAllUploadProgress() {
    return Array.from(this.uploadProgress.entries()).map(([id, progress]) => ({
      id,
      ...progress
    }));
  }

  // Clear completed uploads from progress tracking
  clearCompletedUploads() {
    for (const [id, progress] of this.uploadProgress.entries()) {
      if (progress.status === 'completed' || progress.status === 'error') {
        this.uploadProgress.delete(id);
      }
    }
  }

  // Cancel upload (if supported by server)
  cancelUpload(uploadId) {
    const progress = this.uploadProgress.get(uploadId);
    if (progress) {
      this.uploadProgress.set(uploadId, {
        ...progress,
        status: 'cancelled'
      });
    }
  }

  // Generate file thumbnail (for images)
  async generateThumbnail(file, maxWidth = 200, maxHeight = 200) {
    return new Promise((resolve, reject) => {
      if (!file.type.startsWith('image/')) {
        reject(new Error('File is not an image'));
        return;
      }

      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      const img = new Image();

      img.onload = () => {
        // Calculate new dimensions
        let { width, height } = img;
        
        if (width > height) {
          if (width > maxWidth) {
            height = (height * maxWidth) / width;
            width = maxWidth;
          }
        } else {
          if (height > maxHeight) {
            width = (width * maxHeight) / height;
            height = maxHeight;
          }
        }

        canvas.width = width;
        canvas.height = height;

        // Draw image
        ctx.drawImage(img, 0, 0, width, height);

        // Convert to blob
        canvas.toBlob(resolve, 'image/jpeg', 0.8);
      };

      img.onerror = reject;
      img.src = URL.createObjectURL(file);
    });
  }
}

// Export singleton instance
export const fileManager = new FileManager();
export default fileManager;