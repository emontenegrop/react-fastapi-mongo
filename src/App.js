
import './App.css';
import {useState} from 'react'
import PageWrapper from './components/PageWrapper';
import Paginacion from './components/Paginacion';
import Pelicula from './components/Pelicula';
import peliculasJson from './util/Peliculas.json'


function App() {

  const [paginaActual,setPaginaActual] = useState(1);
  
  let peliculas = peliculasJson;


  peliculas = peliculas.slice((paginaActual -1) * 5 , (paginaActual - 1) * 5 + 5)

  const 

  return (
    <PageWrapper>

      {peliculas.map(pelicula =>
        <Pelicula titulo={pelicula.titulo} calificacion={pelicula.calificacion}
          director={pelicula.director} actores={pelicula.actores}
          fecha={pelicula.fecha} duracion={pelicula.duracion} imagen={pelicula.imagen}>
          {pelicula.descripcion}
        </Pelicula>
      )}

      <Paginacion pagina={paginaActual} total={4} onChange={(pagina)=>{
        setPaginaActual(pagina)
      }}>

      </Paginacion>

    </PageWrapper >


  );
}

export default App;
