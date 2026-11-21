# Calculadora de oro y plata

[Deutsch — Gold- und Silberrechner](https://github.com/media-vm/gold-silber-rechner/tree/main)

Calcula el valor del metal de una joya, moneda o lingote según su peso en
gramos, su pureza en milésimas y el precio por onza troy. La aplicación
muestra el resultado en euros, el peso de metal puro y su equivalente en
onzas troy.

## Descargar

La [versión 2.2 en español](https://github.com/media-vm/gold-silber-rechner/releases/tag/v2.2-es)
incluye un paquete DEB para Debian y Ubuntu, un ZIP con el código, las
dependencias y las instrucciones, y el archivo Python por separado.

## Ejecutar desde el código fuente

Esta edición en español está disponible como código fuente de la rama
`es`. Para ejecutarla necesitas Python 3, Tkinter y un entorno virtual.
En Debian y Ubuntu, instala `python3-tk` y `python3-venv` si te faltan.

```sh
git clone --branch es --single-branch https://github.com/media-vm/gold-silber-rechner.git
cd gold-silber-rechner
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python gold-silver-value-calculator-german-v2.2.py --lang es
```

En Windows, puedes crear el entorno con `py -m venv .venv` y usar
`./.venv/Scripts/python.exe` en lugar de `python` en los dos últimos
comandos. Si prefieres descargar el código sin Git, usa
[el ZIP de la rama es](https://github.com/media-vm/gold-silber-rechner/archive/refs/heads/es.zip).

El programa usa el idioma del sistema para elegir entre español y alemán.
Puedes elegir el idioma de forma explícita con `--lang es` o `--lang de`.

## Calcular el valor de una pieza

1. Elige **Oro** o **Plata**.
2. Introduce el peso total en gramos y selecciona la pureza en milésimas (‰).
   Por ejemplo, 100 g de plata de ley de 925 milésimas contienen 92,5 g de plata pura.
3. Usa la cotización en euros por onza troy o introduce tu propio precio en EUR.
4. Pulsa **Calcular**.

Se admiten números como `1234,56`, `1234.56`, `1.234,56` y `1,234.56`.
Si el número tiene un solo separador, se interpreta como decimal. Escribe
los enteros sin separador de miles, por ejemplo `1234`. La hora de la
cotización se muestra en UTC. El cálculo estima el valor del metal.
El valor de colección, la mano de obra y los márgenes comerciales quedan
fuera del cálculo.

## Paquetes y licencia

Los [paquetes publicados en la versión alemana v2.2](https://github.com/media-vm/gold-silber-rechner/releases/tag/v2.2)
son los de la edición anterior en alemán. En Debian o Ubuntu puedes construir
el paquete bilingüe `2.2-3` con `python3 packaging/build-deb.py`. Se genera
en `dist/`.

El proyecto de Volker Andreas Müller se distribuye bajo la [licencia MIT](LICENSE).
