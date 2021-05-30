import json
import numpy as np
from scipy.io import wavfile
import threading
from scipy.fft import fft, fftfreq, fftshift
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg





class Operacion():
    def __init__(self,samplerate):
        super().__init__()
        self.sameplerate = samplerate
        
    """
    def runEspectro(self):
        global data
        global fft_calculada
        while(1):
            if len(data) > self.MUESTRAS_ANALIZAR:
                datos_analizar = data[0:self.MUESTRAS_ANALIZAR]
                data = data[self.MUESTRAS_ANALIZAR:]
                fft_calculada = self.calcularEspectro(datos_analizar,self.SAMPLERATE)
    """
    def calcularEspectro(self, datos):
        #se quita el ultimo valor 
        frecuencia = datos[-1]
        datos = datos[:-1]
        fft_data = np.fft.fft(datos)/len(datos)
        fft_data = np.fft.fftshift(np.abs(fft_data))
        fft_data_db = 20*np.log10(np.abs(fft_data))
        
        vector_frecuencia = (np.linspace(-0.5,0.5,len(datos))*self.samplerate)+frecuencia
        
        return np.column_stack((fft_data, vector_frecuencia,fft_data_db))

class Graficas():
    def __init__(self):
        super().__init__()
       
        self.primera_vez = True

    def mostrarGrafica(self):
        global datosMostrar
        
       
        self.curve.setData(np.abs(datosMostrar[:,0]))                     # set the curve with this data
        self.curve.setPos(-(len(datosMostrar[:,1])/2),0)                   # set x position in the graph to 0
        QtGui.QApplication.processEvents()

    def runGraficas(self):
        app = QtGui.QApplication([])      
        self.seguir = True

        self.win = pg.GraphicsWindow(title="Analisis espectral") # creates a window
        self.p = self.win.addPlot(title="Fft")  # creates empty space for the plot in the window
        self.curve = self.p.plot() 
        while self.seguir:
           self.mostrarGrafica() 
    def close(self):
        self.seguir = False
        pg.QtGui.QApplication.exec_()         
class Controller():
    def inicializarPlaca(self,frecuenciaPortadoraRecv,frecuenciaPortadoraTrans,samplerate,filtroAnalog,ganancia):
        import adi
        self.placaPluto = adi.Pluto()
        #se ponen los valores por defecto a la placa, para poder recibir una señal 
        setPortadoraRecepcion(frecuenciaPortadoraRecv)
        setPortadoraTransmision(frecuenciaPortadoraTrans)
        setSampleRate(samplerate)
        setFiltroAnalogico(filtroAnalog)
        setControladorGanancia(ganancia)

    def setSampleRate(self,samplerate):
        self.placaPluto.sample_rate = samplerate
    def setPortadoraRecepcion(self,frecuencia):
        self.placaPluto.rx_lo=frecuencia
    def setPortadoraTransmision(self,frecuencia):
        self.placaPluto.tx_lo = frecuencia
    def setGananciaRecepcion(self,ganancia):
        if getControladorGanancia() == "manual":
            self.placaPluto.rx_hardwaregain_chan0 = ganancia
    def setControladorGanancia(self,modo):
        if modo == "slow_attack" or modo == "fast_attack" or modo == "manual":
            self.placaPluto.gain_control_mode_chan0 = modo
    def getControladorGanancia(self,):
        return self.placaPluto.gain_control_mode_chan0
    def setFiltroAnalogico(self,frecuencia):
        self.placaPluto.rx_rf_bandwidth =frecuencia
    def gettFiltroAnalogico(self):
        return self.placaPluto.rx_rf_bandwidth
    def setFiltro(self,filtro):
        self.placaPluto.filter(filtro)
    def rx(self):
        return self.placaPluto.rx()
class Sistema():
    def __init__(self,saltoFrecuencias,frecuenciaMin,frecuenciaMax):
        super().__init__()
        self.saltoFrecuencia = saltoFrecuencias
        self.frecuenciaMin = frecuenciaMin
        self.frecuenciaMax = frecuenciaMax

    def analizarEspectroFrecuencia(self,arrayDatos,arrayFrecuencias,threshold):
        frecuencia = -1
        for i in range(0,len(arrayDatos)):
            if arrayDatos[i] > threshold:
                #en el caso de que un valor sea superior al esperado, busca la frecuencia
                frecuencia = arrayFrecuencias[i]
        return frecuencia
    def decidirFrecuenciaPortadora(self,frecuenciaActual,arrayDatos,arrayFrecuencia,threshold):
        encontrado = False
        frecuenciaResultado = self.analizarEspectroFrecuencia(arrayDatos,arrayFrecuencia,threshold)
        if frecuenciaResultado<0:
            #eso significa que la banda que se ha analizado no tiene nada de interés
            if frecuenciaActual+self.saltoFrecuencia> self.frecuenciaMax+self.saltoFrecuencia:
                frecuenciaPortadora = self.frecuenciaMin
            else:
                frecuenciaPortadora = frecuenciaActual+self.saltoFrecuencia
        else:
            #hay algo de interés, por lo tanto se mueve la frecuencia de portadora para que la banda de interés se encuentre en el centro del espectro
            frecuenciaPortadora = frecuenciaResultado
            encontrado = True

        return frecuenciaPortadora,encontrado

    def analizarEspectro(self,arrayDatos,arrayFrecuencias ,f_target, f_threshold, f_carrier, samplerate):

        f = f_target - f_carrier # frecuencia buscada 
        delta_f = samplerate / (len(arrayDatos) - 1) # intervalo entre frec. 
        pos = (f - samplerate) / delta_f # posicion del valor de la frecuencia buscado

        if arrayFrecuencias(pos) >= f_threshold:
            return True
        else:
            return False
    def generarRuido(self,media,varianza,longitud):
        return np.random.normal(media,varianza,longitud)



	    


        

