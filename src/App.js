
import './App.css';
import { useState } from 'react'
import PageWrapper from './components/PageWrapper';
import Paginacion from './components/Paginacion';
import Pelicula from './components/Pelicula';



function App() {

  const [paginaActual, setPaginaActual] = useState(1);
  const [peliculas, setPeliculas] = useState([]);

  const TOTAL_POR_PAGINA = 4;


  const buscarPeliculas = async () => {
    let url = 'http://localhost/prueba/Peliculas.json';
    //Funcion asincronica
    let respuesta = await fetch(url, {
      'method': 'GET',
      'mode':'no-cors',
      'headers': {
        'Accept': 'application/json',        
        'Content-Type': 'application/json; charset=utf-8'
      }
    });

    let peliculasJson = await respuesta.json();
    setPeliculas(peliculasJson);
  };


  const cargarPelicualas = () => {
    /* peliculas = peliculas.slice(
       (paginaActual - 1) * TOTAL_POR_PAGINA,
       (paginaActual * TOTAL_POR_PAGINA)
     );*/
  }

  const getTotalPaginas = () => {
    let cantidadTotalPeliculas = peliculas.length;
    return Math.ceil(cantidadTotalPeliculas / TOTAL_POR_PAGINA)
  }



  return (
    <PageWrapper>
      <button onClick={buscarPeliculas}>Prueba</button>

      {peliculas.map(pelicula =>
        <Pelicula titulo={pelicula.titulo} calificacion={pelicula.calificacion}
          director={pelicula.director} actores={pelicula.actores}
          fecha={pelicula.fecha} duracion={pelicula.duracion} imagen={pelicula.imagen}>
          {pelicula.descripcion}
        </Pelicula>
      )}

      <Paginacion pagina={paginaActual} total={getTotalPaginas()} onChange={(pagina) => {
        setPaginaActual(pagina)
      }}>

      </Paginacion>

    </PageWrapper >


  );
}

export default App;
