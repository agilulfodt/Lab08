from datetime import datetime

from database.impianto_DAO import ImpiantoDAO

'''
    MODELLO:
    - Rappresenta la struttura dati
    - Si occupa di gestire lo stato dell'applicazione
    - Interagisce con il database
'''

class Model:
    def __init__(self):
        self._impianti = None
        self.load_impianti()

        self.__sequenza_ottima = []
        self.__costo_ottimo = -1

    def load_impianti(self):
        """ Carica tutti gli impianti e li setta nella variabile self._impianti """
        self._impianti = ImpiantoDAO.get_impianti()

    def get_consumo_medio(self, mese:int):
        """
        Calcola, per ogni impianto, il consumo medio giornaliero per il mese selezionato.
        :param mese: Mese selezionato (un intero da 1 a 12)
        :return: lista di tuple --> (nome dell'impianto, media), es. (Impianto A, 123)
        """
        # TODO
        lista = [] #lista di tuple
        for impianto in self._impianti:
            impianto.get_consumi()
            n_consumi = 0
            sum_consumi = 0
            for consumo in impianto.lista_consumi:
                if consumo.data.month == mese:
                    n_consumi += 1
                    sum_consumi += consumo.kwh
            media = sum_consumi / n_consumi
            lista.append((impianto.nome, media))
        return lista


    def get_sequenza_ottima(self, mese:int):
        """
        Calcola la sequenza ottimale di interventi nei primi 7 giorni
        :return: sequenza di nomi impianto ottimale
        :return: costo ottimale (cioè quello minimizzato dalla sequenza scelta)
        """
        self.__sequenza_ottima = []
        self.__costo_ottimo = -1
        consumi_settimana = self.__get_consumi_prima_settimana_mese(mese)

        self.__ricorsione([], 1, None, 0, consumi_settimana)

        # Traduci gli ID in nomi
        id_to_nome = {impianto.id: impianto.nome for impianto in self._impianti}
        sequenza_nomi = [f"Giorno {giorno}: {id_to_nome[i]}" for giorno, i in enumerate(self.__sequenza_ottima, start=1)]
        return sequenza_nomi, self.__costo_ottimo

    def __ricorsione(self, sequenza_parziale, giorno, ultimo_impianto, costo_corrente, consumi_settimana):
        """ Implementa la ricorsione """
        # TODO
        if giorno == 8:
            if self.__costo_ottimo == -1 or costo_corrente < self.__costo_ottimo:
                self.__costo_ottimo = costo_corrente
                self.__sequenza_ottima = sequenza_parziale.copy()
            return

        for impianto_id, consumi in consumi_settimana.items():
            consumo_giorno = consumi[giorno - 1]
            costo_spostamento = 0
            if ultimo_impianto is not None and ultimo_impianto != impianto_id:
                costo_spostamento = 5
            nuovo_costo = costo_corrente + consumo_giorno + costo_spostamento
            sequenza_parziale.append(impianto_id)
            self.__ricorsione(sequenza_parziale, giorno + 1, impianto_id, nuovo_costo, consumi_settimana)
            sequenza_parziale.pop()

    def __get_consumi_prima_settimana_mese(self, mese: int):
        """
        Restituisce i consumi dei primi 7 giorni del mese selezionato per ciascun impianto.
        :return: un dizionario: {id_impianto: [kwh_giorno1, ..., kwh_giorno7]}
        """
        # TODO
        dizio = {}
        for impianto in self._impianti:
            impianto.get_consumi()
            lista_consumi_prima_settimana = []
            for consumo in impianto.lista_consumi:
                if consumo.data.day <= 7 and consumo.data.month == mese:
                    lista_consumi_prima_settimana.append(consumo.kwh)
                elif len(lista_consumi_prima_settimana) == 7:
                    break
            dizio[impianto.id] = lista_consumi_prima_settimana
        return dizio