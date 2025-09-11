from datetime import datetime
from typing import Optional
from fastapi import APIRouter, status, HTTPException, Query
from fastapi.responses import JSONResponse

from app.config.messages import Messages
from app.utils.exceptions import DetailHttpException
from app.utils.health_checks import health_manager, HealthStatus
from app.utils.structured_logger import get_logger
from app.db.database import db

logger = get_logger("health_endpoints")

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/", status_code=200, summary="Basic health check", description="Simple health check that tests database connectivity")
async def basic_health_check():
    """Basic health check with database connectivity test"""
    try:
        # Test database with a simple operation (legacy compatibility)
        temp_doc = {"created_at": datetime.now()}
        result = await db.health_check.insert_one(temp_doc)
        current_date_time = await db.health_check.find_one({"_id": result.inserted_id})
        await db.health_check.delete_one({"_id": current_date_time["_id"]})

        if current_date_time:
            logger.info("Basic health check passed")
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "status": "healthy",
                    "date": current_date_time["created_at"].strftime("%Y-%m-%d"),
                    "time": current_date_time["created_at"].strftime("%H:%M:%S"),
                    "message": "Service is healthy"
                }
            )
        else:
            raise DetailHttpException(
                status.HTTP_424_FAILED_DEPENDENCY, 
                Messages.INVALID_HEALTH_CHECK
            )
            
    except Exception as e:
        logger.error("Basic health check failed", error=str(e))
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "message": f"Health check failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
        )


@router.get("/detailed", summary="Comprehensive health check", description="Comprehensive health check covering all system components")
async def comprehensive_health_check(force: bool = Query(False, description="Force running checks even if cached")):
    """Comprehensive health check covering all system components"""
    try:
        results = await health_manager.run_all_checks(force=force)
        
        # Determine HTTP status code based on overall health
        http_status = status.HTTP_200_OK
        if results["overall_status"] == HealthStatus.CRITICAL:
            http_status = status.HTTP_503_SERVICE_UNAVAILABLE
        elif results["overall_status"] == HealthStatus.UNHEALTHY:
            http_status = status.HTTP_503_SERVICE_UNAVAILABLE
        elif results["overall_status"] == HealthStatus.DEGRADED:
            http_status = status.HTTP_200_OK  # Still operational but degraded
        
        return JSONResponse(
            status_code=http_status,
            content=results
        )
        
    except Exception as e:
        logger.error("Comprehensive health check failed", error=str(e))
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "overall_status": HealthStatus.CRITICAL,
                "overall_message": f"Health check system failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
        )


@router.get("/check/{check_name}", summary="Single health check", description="Run a specific health check by name")
async def single_health_check(check_name: str):
    """Run a single health check by name"""
    try:
        result = await health_manager.run_single_check(check_name)
        
        if result is None:
            available_checks = health_manager.get_check_names()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Health check '{check_name}' not found. Available checks: {', '.join(available_checks)}"
            )
        
        # Determine HTTP status based on check result
        http_status = status.HTTP_200_OK
        if result["status"] == HealthStatus.CRITICAL:
            http_status = status.HTTP_503_SERVICE_UNAVAILABLE
        elif result["status"] == HealthStatus.UNHEALTHY:
            http_status = status.HTTP_503_SERVICE_UNAVAILABLE
        
        return JSONResponse(
            status_code=http_status,
            content=result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Single health check failed", check_name=check_name, error=str(e))
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "name": check_name,
                "status": HealthStatus.CRITICAL,
                "message": f"Health check failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
        )


@router.get("/checks", summary="List available health checks", description="Get list of all available health checks")
async def list_health_checks():
    """Get list of all available health checks"""
    try:
        check_names = health_manager.get_check_names()
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "success",
                "data": {
                    "available_checks": check_names,
                    "total_checks": len(check_names)
                },
                "message": "Available health checks retrieved successfully"
            }
        )
        
    except Exception as e:
        logger.error("Failed to list health checks", error=str(e))
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "error",
                "message": f"Failed to retrieve health checks: {str(e)}"
            }
        )


@router.get("/status", summary="Health status summary", description="Get a quick summary of system health status")
async def health_status_summary():
    """Get a quick summary of system health status"""
    try:
        results = await health_manager.run_all_checks()
        
        # Extract key metrics for dashboard/monitoring
        summary = {
            "status": results["overall_status"],
            "message": results["overall_message"],
            "timestamp": results["timestamp"],
            "checks_summary": results["summary"],
            "critical_systems": []
        }
        
        # Add details about critical systems
        for check in results["checks"]:
            if check["critical"] and check["status"] in [HealthStatus.UNHEALTHY, HealthStatus.CRITICAL]:
                summary["critical_systems"].append({
                    "name": check["name"],
                    "status": check["status"],
                    "message": check["message"]
                })
        
        http_status = status.HTTP_200_OK
        if results["overall_status"] in [HealthStatus.CRITICAL, HealthStatus.UNHEALTHY]:
            http_status = status.HTTP_503_SERVICE_UNAVAILABLE
        
        return JSONResponse(
            status_code=http_status,
            content=summary
        )
        
    except Exception as e:
        logger.error("Health status summary failed", error=str(e))
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": HealthStatus.CRITICAL,
                "message": f"Health status check failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
        )
