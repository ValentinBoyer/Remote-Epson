import os  # Module pour gérer les opérations liées au système de fichiers
import sys  # Module pour interagir avec le système et les arguments de ligne de commande

import serial.tools.list_ports  # Permet de lister les ports série disponibles
from wx import xrc  # Permet de charger des fichiers d'interface au format XML
import wx  # Framework pour créer des interfaces graphiques

# Dictionnaire associant les boutons de l'interface graphique à leurs codes de commande
KEYCODES = {
    'buttonComputer': '43',  # Bouton pour commuter sur l'entrée ordinateur
    'buttonVideo': '48',     # Bouton pour commuter sur l'entrée vidéo
    'buttonColour': '3f',    # Bouton pour ajuster les couleurs
    'buttonMenu': '3c',      # Bouton pour ouvrir le menu
    'buttonMute': '3e',      # Bouton pour couper le son
    'buttonFreeze': '47',    # Bouton pour geler l'image
    'buttonMinus': '29',     # Bouton pour diminuer une valeur
    'buttonPlus': '28',      # Bouton pour augmenter une valeur
    'buttonUp': '58',        # Bouton flèche haut
    'buttonDown': '59',      # Bouton flèche bas
    'buttonLeft': '5a',      # Bouton flèche gauche
    'buttonRight': '5b',     # Bouton flèche droite
    'buttonEnter': '49',     # Bouton "Entrer"
    'buttonAuto': '4a',      # Bouton pour ajustement automatique
    'buttonEsc': '3d'        # Bouton "Echap"
}

# Classe principale de l'interface utilisateur
class FrameMain(wx.Frame):
    def __init__(self):
        # Initialisation de la fenêtre principale
        wx.Frame.__init__(self, None, title='VP21 RC',
                          style=wx.CAPTION |  # Ajoute une barre de titre
                          wx.CLOSE_BOX |     # Permet de fermer la fenêtre
                          wx.FRAME_TOOL_WINDOW)  # Style compact de fenêtre

        self._serial = None  # Instance pour gérer la connexion série

        # Charge l'interface utilisateur depuis le fichier XML
        ui = self.__load_ui('main.xrc')
        ui.LoadPanel(self, 'Panel')  # Insère un panneau dans la fenêtre

        # Ajoute une barre d'état pour afficher des messages à l'utilisateur
        self._status = wx.StatusBar(self, style=wx.STB_SHOW_TIPS)
        self.SetStatusBar(self._status)

        self._buttons = []  # Liste pour stocker les identifiants des boutons

        # Ajout du bouton d'alimentation (Power)
        cid = xrc.XRCID('buttonPower')
        self._buttons.append(cid)
        self.Bind(wx.EVT_BUTTON, self.__on_power, id=cid)  # Associe une action au bouton Power

        # Ajout des autres boutons définis dans KEYCODES
        for name, code in KEYCODES.iteritems():
            cid = xrc.XRCID(name)  # Récupère l'identifiant du bouton
            self._buttons.append(cid)
            # Associe chaque bouton à une fonction avec son code
            self.Bind(wx.EVT_BUTTON,
                      lambda evt, code=code: self.__on_button(evt, code),
                      id=cid)

        # Liste les ports série disponibles
        ports = [port[0] for port in serial.tools.list_ports.comports()]
        choiceSerial = xrc.XRCCTRL(self, 'choiceSerial')  # Récupère la liste déroulante
        choiceSerial.AppendItems(ports)  # Ajoute les ports trouvés
        if len(ports):  # Si des ports sont disponibles
            choiceSerial.SetSelection(0)  # Sélectionne le premier port par défaut
            self.Bind(wx.EVT_CHOICE, self.__on_serial, choiceSerial)  # Associe une action au choix d'un port
            self.__open_serial()  # Ouvre la connexion série

        self.Fit()  # Ajuste la taille de la fenêtre
        self.Show()  # Affiche la fenêtre

    def __on_power(self, _event):
        # Vérifie l'état du vidéoprojecteur
        self._serial.write('PWR?\r\n')  # Envoie la commande pour interroger l'état d'alimentation
        resp = self._serial.readall()  # Lit la réponse
        if 'PWR=01' in resp:  # Si le projecteur est allumé
            self._serial.write('PWR OFF\r\n')  # Envoie la commande pour l'éteindre
        else:  # Sinon
            self._serial.write('PWR ON\r\n')  # Envoie la commande pour l'allumer

    def __on_button(self, _event, code):
        # Envoie une commande correspondant au bouton cliqué
        if self._serial is not None and self._serial.is_open:
            try:
                self._serial.write('KEY ' + code + '\r\n')  # Envoie le code du bouton
            except serial.SerialException as e:
                self._status.SetStatusText(e.message)  # Affiche un message d'erreur dans la barre d'état

    def __on_serial(self, _event):
        # Gère le choix d'un port série
        self.__open_serial()

    def __open_serial(self):
        # Ouvre une connexion série
        choiceSerial = xrc.XRCCTRL(self, 'choiceSerial')
        port = choiceSerial.GetStringSelection()  # Récupère le port sélectionné
        if self._serial is not None:
            try:
                self._serial.close()  # Ferme une éventuelle connexion existante
            except serial.SerialException:
                pass

        self.__buttons_enable(False)  # Désactive les boutons pendant la tentative de connexion

        try:
            # Crée une nouvelle connexion série avec les paramètres par défaut
            self._serial = serial.Serial(port,
                                         9600,  # Vitesse en bauds
                                         timeout=0.5,  # Délai d'attente
                                         write_timeout=0)  # Pas de délai d'écriture
            self._serial.reset_input_buffer()  # Vide le tampon d'entrée
            self._serial.reset_output_buffer()  # Vide le tampon de sortie
        except serial.SerialException as e:
            self._status.SetStatusText(e.message)  # Affiche une erreur dans la barre d'état
            return

        self.__buttons_enable(True)  # Active les boutons si la connexion réussit
        self._status.SetStatusText('Connected')  # Affiche un message de connexion réussie

    def __buttons_enable(self, enable):
        # Active ou désactive les boutons en fonction de l'état de connexion
        for cid in self._buttons:
            self.FindWindowById(cid).Enable(enable)

    def __get_ui_dir(self):
        # Détermine le répertoire contenant les fichiers d'interface utilisateur
        if getattr(sys, 'frozen', False):  # Si le programme est exécuté en tant que binaire
            resDir = os.path.join(sys._MEIPASS, 'ui')  # Répertoire temporaire
        else:  # Sinon, mode développement
            scriptDir = os.path.dirname(os.path.realpath(sys.argv[0]))
            resDir = os.path.join(scriptDir, 'gui', 'ui')

        return resDir  # Retourne le chemin du répertoire UI

    def __load_ui(self, filename):
        # Charge un fichier d'interface utilisateur au format XML
        path = os.path.join(self.__get_ui_dir(), filename)
        return xrc.XmlResource(path)  # Retourne l'objet ressource
