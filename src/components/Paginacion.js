import React from 'react';

export default function Paginacion(props) {


    const getPaginas = () => {
        const resultado = [];
        for (var i = 0; i < props.total; i++) {
            let pagina = i + 1;
            resultado.push(
                <a onClick={() => props.onChange(pagina)}
                    className={props.pagina === pagina ? 'active' : ''} href="#">{pagina}
                </a>
            );
        }
        return resultado;
    }

    return (

        <div className="topbar-filter">
            <label>Movies per page:</label>
            <div className="pagination2">
                <span>pagina {props.pagina} de {props.total}:</span>
                {getPaginas()}
                <a href="#"><i className="ion-arrow-right-b"></i></a>
            </div>
        </div>

    );
}