# Calculadora de oro y plata

[Deutsch — Gold- und Silberrechner](README.md)

Calcula el valor del metal de una joya, moneda o lingote según su peso en
gramos, su pureza en milésimas y el precio por onza troy. La aplicación
muestra el resultado en la moneda elegida, el peso de metal puro y su equivalente en
onzas troy.

## Descargar

La [versión 2.3](https://github.com/media-vm/gold-silber-rechner/releases/tag/v2.3) ofrece los mismos archivos para español y alemán:

- [Windows 10 y 11 (64 bits)](https://github.com/media-vm/gold-silber-rechner/releases/download/v2.3/Gold-Silber-Rechner-2.3.exe)
- [Windows 7 (32 bits)](https://github.com/media-vm/gold-silber-rechner/releases/download/v2.3/Gold-Silber-Rechner-2.3-Windows7.exe)
- [Paquete DEB 2.3-1 para Debian y Ubuntu](https://github.com/media-vm/gold-silber-rechner/releases/download/v2.3/gold-silber-rechner_2.3-1_all.deb)

Los ejecutables tienen la firma del autor y un sello de tiempo de DigiCert. La aplicación usa el idioma del sistema. Puedes forzar el español con `--lang es`.

## Instalar desde Snap Store

La [Calculadora de oro y plata](https://snapcraft.io/gold-silber-rechner)
está disponible como versión 2.3 en `latest/stable` para amd64 (revisión 11) y ARM64 (revisión 10). En un sistema con
Snap instalado:

```sh
sudo snap install gold-silber-rechner
snap run gold-silber-rechner --lang es
```

Si ya tienes la aplicación, actualízala con
`sudo snap refresh gold-silber-rechner --channel=latest/stable`. En sistemas
configurados en español, el menú muestra «Calculadora de oro y plata».

## Ejecutar desde el código fuente

La interfaz en español comparte el mismo código Python que la alemana.
La versión de desarrollo se mantiene en `main`. Para ejecutarla necesitas Python 3, Tkinter y un entorno virtual.
En Debian y Ubuntu, instala `python3-tk` y `python3-venv` si te faltan.

```sh
git clone --branch main --single-branch https://github.com/media-vm/gold-silber-rechner.git
cd gold-silber-rechner
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python gold-silver-value-calculator-german-v2.2.py --lang es
```

En Windows, puedes crear el entorno con `py -m venv .venv` y usar
`./.venv/Scripts/python.exe` en lugar de `python` en los dos últimos
comandos. Si prefieres descargar el código sin Git, usa
[el ZIP de la rama main](https://github.com/media-vm/gold-silber-rechner/archive/refs/heads/main.zip).

El programa usa el idioma del sistema para elegir entre español y alemán.
Puedes elegir el idioma de forma explícita con `--lang es` o `--lang de`.

## Calcular el valor de una pieza

1. Elige **Oro** o **Plata**.
2. Introduce el peso y elige la unidad. Los gramos son la opción inicial.
   Selecciona la pureza en milésimas (‰), con indicaciones de quilates para
   el oro y una opción de dineros y granos para la plata histórica.
   Por ejemplo, 100 g de plata de ley de 925 milésimas contienen 92,5 g de plata pura.
3. Selecciona una de las 19 monedas. Usa la cotización convertida por onza troy o introduce un precio en la moneda seleccionada.
4. Pulsa **Calcular**.

Se admiten números como `1234,56`, `1234.56`, `1.234,56` y `1,234.56`.
Si el número tiene un solo separador, se interpreta como decimal. Escribe
los enteros sin separador de miles, por ejemplo `1234`. La hora de la
cotización se muestra en UTC. El cálculo estima el valor del metal.
El valor de colección, la mano de obra y los márgenes comerciales quedan
fuera del cálculo.

## Paquetes y licencia

En Debian o Ubuntu puedes construir el paquete `2.3-1` con
`python3 packaging/build-deb.py`. Se genera en `dist/`.

El proyecto de Volker Andreas Müller se distribuye bajo la [licencia MIT](LICENSE).
