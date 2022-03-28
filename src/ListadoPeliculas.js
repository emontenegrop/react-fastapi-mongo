
import './App.css';
import { React, useEffect, useState } from 'react'
import PageWrapper from './components/PageWrapper';
import Paginacion from './components/Paginacion';
import Pelicula from './components/Pelicula';



function ListadoPeliculas() {

    const [paginaActual, setPaginaActual] = useState(1);
    const [peliculas, setPeliculas] = useState([]);

    useEffect(() => {
        buscarPeliculas();
    }, []);

    const TOTAL_POR_PAGINA = 4;

    const buscarPeliculas2 = async () => {
        let url = 'http://localhost:5000/listado';
        //Funcion asincronica
        let respuesta = await fetch(url, {
            'method': 'GET',
            'mode': 'no-cors',
            'headers': {
                'Accept': 'application/json',
                'Content-Type': 'application/json; charset=utf-8'
            }
        });
    };

    const buscarPeliculas = async () => {
        const rawResponse = await fetch('http://localhost:8000/listado');
        let response = await rawResponse.json();
        //const content =  prueba.json();

        console.log(response);
        setPeliculas(response)

    };


    const buscarPeliculas3 = async () => {
        const rawResponse = await fetch('https://httpbin.org/get', {
            method: 'GET',
            mode: 'no-cors',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }//,
            //body: JSON.stringify({ a: 1, b: 'Textual content' })
        });

        let prueba = await JSON.parse(rawResponse);
        const content = prueba.json();

        console.log(content);
    };

    const buscarPeliculasPOST = async () => {
        const rawResponse = await fetch('https://httpbin.org/post', {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ a: 1, b: 'Textual content' })
        });
        const content = await rawResponse.json();

        console.log(content);
    };

    const getTotalPaginas = () => {
        let cantidadTotalPeliculas = peliculas.length;
        return Math.ceil(cantidadTotalPeliculas / TOTAL_POR_PAGINA)
    }

    let peliculasXPagina = peliculas.slice(
        (paginaActual - 1) * TOTAL_POR_PAGINA,
        (paginaActual * TOTAL_POR_PAGINA)
    );

    return (
        <PageWrapper>
            <button onClick={buscarPeliculas}>Prueba</button>

            {peliculasXPagina.map(pelicula =>
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

export default ListadoPeliculas;
