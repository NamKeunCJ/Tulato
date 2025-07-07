document.querySelectorAll('.grafica-vereda').forEach(div => {
    const vereda = div.dataset.vereda;
    const ejey = div.dataset.ejey;
    const datos = [
        parseInt(div.dataset.cantidad1),
        parseInt(div.dataset.cantidad2),
        parseInt(div.dataset.cantidad3)
    ];
    const bases = [
        div.dataset.base1,
        div.dataset.base2,
        div.dataset.base3
    ];

    const options = {
        series: [{
            name: "Datos",
            data: datos
        }],
        chart: {
            height: 250,
            type: 'bar',
            zoom: { enabled: false },
            toolbar: {
                show: true,
                tools: {
                    download: true
                },
                export: {
                    csv: {
                        filename: `${vereda}`
                    },
                    svg: {
                        filename: `${vereda}`
                    },
                    png: {
                        filename: `${vereda}`
                    }
                }
            },
        },
        colors: ['#EBAC06'], 
        dataLabels: {
            enabled: true,
            position: 'top', 
            style: {
                fontSize: '12px',
                colors: ['#926901'] 
            }
        },

        title: {
            text: `${vereda}`,
            align: 'left'
        },
        xaxis: {
            categories: bases
        },
        yaxis: {
            labels: {
                formatter: function (val) {
                    return Number.isInteger(val) ? val : '';
                }
            },
            title: {
                text: ejey,
                offsetX: 5,
                style: {
                    fontSize: '14px',
                    fontWeight: 'bold',
                    color: '#333'
                }
            },
        },
        grid: {
            row: {
                colors: ['#f3f3f3', 'transparent'],
                opacity: 0.5
            }
        }
    };

    const chart = new ApexCharts(div, options);
    chart.render();
});

document.querySelectorAll('.grafica-torta').forEach(div => {
    const titulo = div.dataset.titulo;
    const acierto = parseFloat(div.dataset.acierto);
    const error = parseFloat(div.dataset.error);

    const options = {
        chart: {
            type: 'pie',
            width: 380,
            toolbar: {
                show: true,
                tools: {
                download: true
                },
                export: {
                csv: {
                    filename: `aciertos_errores_${titulo}`
                },
                svg: {
                    filename: `aciertos_errores_${titulo}`
                },
                png: {
                    filename: `aciertos_errores_${titulo}`
                }
                }
            }                            
        },
        labels: ['Aciertos', 'Errores'],
        series: [acierto, error],
        colors: ['#043b26', '#f4b63f'],
        dataLabels: {
            enabled: true,
            formatter: function (val) {
                return val.toFixed(0) + '%';
            }
        },
        title: {
            text: `Aciertos y Errores - ${titulo}`,
            align: 'center',
            style: {
                fontSize: '14px'
            }
        },
        legend: {
            position: 'bottom'
        }
    };

    const chart = new ApexCharts(div, options);
    chart.render();
});

document.querySelectorAll('.grafica-rendimiento').forEach(div => {
    const titulos = [
        div.dataset.tituloambiental,
        div.dataset.tituloeconomico,
        div.dataset.titulosocial
    ];

    const aciertos = [ 
        parseFloat(div.dataset.aciertoambiental),
        parseFloat(div.dataset.aciertoeconomico),
        parseFloat(div.dataset.aciertosocial)
    ];
    console.log('Títulos:', titulos);
    console.log('Aciertos:', aciertos);
    console.dir(div);

    const options = {
        series: [{
            name: "Promedio de aciertos",
            data: aciertos
        }],
        chart: {
            height: 250,
            type: 'bar',
            zoom: { enabled: false },
            toolbar: {
                show: true,
                tools: {
                    download: true
                },
                export: {
                    csv: {
                        filename: `Rendimiento Test`
                    },
                    svg: {
                        filename: `Rendimiento Test`
                    },
                    png: {
                        filename: `Rendimiento Test`
                    }
                }
            }
        },
        colors: ['#063F23'], 
        dataLabels: {
            enabled: true,
            position: 'top',
            formatter: function (val) {
                return val + '%'; // Agrega el símbolo %
            },
            style: {
                fontSize: '12px',
                colors: ['#fff']
            }
        },

        title: {
            text: `Rendimiento Test`,
            align: 'left'
        },
        xaxis: {
            categories: titulos
        },
        yaxis: {
            title: {
                text: 'Promedio de aciertos',
                style: {
                    fontSize: '14px',
                    fontWeight: 'bold',
                    color: '#333'
                }
            }
        },

        grid: {
            row: {
                colors: ['#f3f3f3', 'transparent'],
                opacity: 0.5
            }
        }
    };

    const chart = new ApexCharts(div, options);
    chart.render();
});