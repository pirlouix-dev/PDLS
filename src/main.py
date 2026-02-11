# -*- coding: utf-8 -*-
# Fait :
# - Lors d'un bug report, envoyer aussi la plateforme
# - Réduire la taille du texte dans les descriptions dans "Modifier" et "Créer" un plat

# Bugs connus :

# Optimisations et améliorations :
# - Dans la liste des plats à modifier, permettre de trier les plats par ordre alphabétique, par type et par saison (en petit écran, sur l'espace du bouton quitter, en grand écran, au dessus du titre en poussant le reste vers le bas) (Le classement est alphabétique (défault) ou par type. Il y a ensuite un file pour sélectionner les saisons (toutes par défault))
# - Lorsqu'il y a une màj, mettre une pastille sur les paramètres. Ça prépare mentalement
# - Lors d'une mise à jour automatique, télécharger les fichiers en amont et ne faire que l'installation
# - Lorsque l'utilisateur n'a aucun plat et souhaite avoir le menu, le lui dire et le retirer du menu
# - Retirer la fonction "Remove Bugs" (ne vaut pas le coup)
# - Faire la transition entre "download-folder" et "download-links" dans l'API
# - Lors des mises à jour, essayer aussi de mettre à jour mes applis sans màj auto si disponibles
# - Faire fonctionner la sélection des saisons avec un seul stylesheet
# - Changer la section "Signaler un bug" pour permettre le signalement d'un bug (expliquer précisément la reproduction), la proposition d'une fonctionalité (et pourquoi) ou une argumentation contre un changement
# - Améliorer le design des boutons radio et normaux (violet c'est moche, le rond violet est très moche, regarder les gradiants pour les stylesheets)
# - Combiner Force Update et No Update Error
# - Faire une transition au noir pour Choose Menu également
# - Faire en sorte que le bouton Delete clique sur "Fermer" dans tous les menus
# - Avoir le même style de boutons partout (celui avec arrière plan Pixlr)
# - Faire marcher le raccourcis clavier plein écran
# - Mettre un bouton "Réessayer" lorsqu'une erreur réseau survient

# Projets long termes :
# - Faire une version Android avec le même code, en adaptant la taille des widgets (il est nécessaire soit d'utiliser les layout, soit de recoder les tailles, car on ne peut pas rétécire artificiellement une appli)
# - Changer la description des plats en deux fonctionalités : les ingredients et la préparation. Repenser l'UI et le fonctionnement avant.
# - Avoir un moyen d'exporter les données une fois la sélection des plats terminée (par mail, sur une application mobile, intégré avec l'applis de liste d'Apple, etc.)
# - Faire payer à partir de 30 plats, et prévenir au moment de la création de plat par une petite bulle quand il en reste moins de 10
# - Corriger bug : Quand on crée / modifie un plat, faire un appui long écrit plein de fois la même chose (= Installer PyQt6 si Spyder ou Anaconda le veux, ou bien installer PySyde6 (comptaible anaconda) ou bien override le keyboard)
# - Essayer d'en faire une version IOS (Se renseigner sur l'éxecution d'Applescript pour mettre la V2 ou Python avec Shortcuts ou ISH)

# Check-liste mises à jour
# - Désactiver les mode Debug, Force update et No update error
# - Changer la version, le nombre de ligne et le timestamp dans le code
# - Sauvegarder les modifications
# - Créer les fichiers d'installation
# - Commit la version sur Github
# - Mettre à jour l'API
# - Mettre à jour mes archives personelles

#%% Global variables
import os
import sys
import time
import traceback
import sip
import json
import webbrowser
import pyperclip
import random
import hashlib
import DPI
from datetime import date, datetime
from packaging.version import Version
from MainModule import RowFadeController
from Dish import Ui_Form as DishModule
from DishWithSettings import Ui_Form as SettingsDishModule
from Backup import Ui_BackupParent as BackupModule
from MainMenu import Ui_MainWindow as MainMenuModule
from ChooseMenu import Ui_MainWindow as ChooseMenuModule
from CreateMenu import Ui_MainWindow as CreateDishModule
from ModifyMenu import Ui_MainWindow as ModifyMenuModule
from SettingsMenu  import Ui_MainWindow as SettingsMenuModule
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QStackedWidget, QVBoxLayout, QMessageBox, QPlainTextEdit, QLineEdit, QGraphicsOpacityEffect, QLabel
from PyQt5.QtTest import QTest
from PyQt5.QtGui import QFontMetrics, QResizeEvent, QFontDatabase
from PyQt5.QtCore import QPoint, QSize, QPropertyAnimation, Qt, QSettings, QTimer, QObject, QEvent, pyqtSignal, QUrl, QByteArray
from PyQt5.QtNetwork import QNetworkRequest, QNetworkAccessManager, QNetworkReply

DEBUG_MODE = False
FORCE_UPDATE = False
NO_UPDATE_ERROR = False

Wait = QTest.qWait
QLabel = QLabel
WidgetDisplayInfo = {}
ImpactedWidgetDisplay = []
CustomResizeFunctions = []
Loading = False
FirstStart = True
KeyOverride = False
KeyOverrideFunc = None
AppVersion = "3.8.1"
LineCount = "3,000"
Timestamp = 1749062742

UpdateCommands = {
    "darwin": "(curl -s https://raw.githubusercontent.com/pirlouix-dev/PDLS/refs/heads/main/Scripts/MacOS.sh > /private/tmp/PDLS_Script.sh; sh /private/tmp/PDLS_Script.sh; rm /private/tmp/PDLS_Script.sh) > /dev/null 2>&1 &",
    "win32": "start /min cmd /c \"curl -s -o PDLS_Installer.bat https://raw.githubusercontent.com/pirlouix-dev/PDLS/refs/heads/main/Scripts/Windows.bat && PDLS_Installer.bat && del PDLS_Installer.bat >nul 2>&1\""
    }
AutoUpdateSupport = sys.platform in ["darwin", "win32"]

APIUrl = "https://676d02470e299dd2ddfe1998.mockapi.io/PDLS/v1"
RequestSuccessful = False
FeedbackURL = None
LatestVersion = None
DownloadFolder = None
UpdateDescription = None

ScreenScaleFactor = DPI.GetDPI()/127.75
ScreenScaleFactor = 1 if ScreenScaleFactor <= 1.1 else ScreenScaleFactor
CompatibilitySize = ScreenScaleFactor != 1

def GetStyleSheet(RGBA):
    RGBA = tuple(RGBA)
    return """
        MainWindow {
            background-color: rgba""" + str(RGBA) + """;
            background-position: center;
        }
        """
        
def Warn(*args):
    print("--------\nWarning: ", *args,"\n--------")

def AddWidgetDisplayInfo(Widget, CenterPositionRatio, SizeRatio, AnchorPoint, AspectRatio, MaximumSizeY=16777215):
    WidgetDisplayInfo[Widget.objectName()] = {
        "CenterPositionRatio": CenterPositionRatio,
        "SizeRatio": SizeRatio,
        "AnchorPoint": AnchorPoint,
        "AspectRatio": AspectRatio,
        "MaximumSizeY": MaximumSizeY
    }
    
def MakeTextFitByCropping(Text, Label, LineCount, TextOffset):
    FontMetrics = QFontMetrics(Label.font())
    LabelRect = Label.contentsRect()
    LabelSize = LabelRect.size()
    TextRect = FontMetrics.boundingRect(LabelRect, Qt.TextWordWrap, Text)
    TextSize = TextRect.size()
    
    if TextSize.height() <= LabelSize.height():
        return Text, True
    
    CropCount = 0
    while TextSize.height() > LabelSize.height():
        CropCount -= max(1, (TextSize.height() - LabelSize.height())//5)
        TextCropped = Text[:CropCount] + "..."
        TextSize = FontMetrics.boundingRect(LabelRect, Qt.TextWordWrap, TextCropped + TextOffset).size()

    return TextCropped, False

def MakeTextFitWithSize(Text, Label, LineCount, Offset):
    Font = Label.font()
    FontMetrics = QFontMetrics(Label.font())
    TextWidth = FontMetrics.horizontalAdvance(Text)
    LabelWidth = Label.width() * LineCount - Offset
    
    if TextWidth <= LabelWidth:
        return Font
    
    while TextWidth > LabelWidth:
        Font.setPixelSize(Font.pixelSize() - 1)
        FontMetrics = QFontMetrics(Font)
        TextWidth = FontMetrics.horizontalAdvance(Text)
            
    return Font

def MessageStyleSheet(MessageBox):
    BackgroundColor = "solid " + MessageBox.palette().window().color().name()
    return """
        QPushButton {
            background-color: rgb(100, 100, 100);
            color: white;
            padding: 7px;
            border-radius: 7px;
            border: 2px """ + BackgroundColor + """;
        }
        QPushButton:focus {
            padding: 5px;
            border: 2px solid rgb(0, 213, 255);
            border-radius: 5px;
        }
        QPushButton:hover {
            background-color: rgb(120, 120, 120);
        }
    """
    
def IsUpdateAvailable():
    if not RequestSuccessful:
        return False
    
    return FORCE_UPDATE or Version(AppVersion) < Version(LatestVersion)
    
def TwoChar(Num):
    Num = str(Num)
    return "0" + Num if len(Num) == 1 else Num

def Plurial(Num):
    return "" if int(Num) in [0,1] else "s"

def OSName(platform):
    if platform == "darwin":
        return "MacOS"
    elif platform == "win32":
        return "Windows"
    else:
        return platform
    
def DEBUG_GetDisplayInfo(FrameSize, ObjectSize, ObjectPos, AnchorPoint):
    Size = (ObjectSize[0]/FrameSize[0], ObjectSize[1]/FrameSize[1])
    CenterPos = (ObjectPos[0] + ObjectSize[0]*AnchorPoint[0], ObjectPos[1] + ObjectSize[1]*AnchorPoint[1])
    Pos = (CenterPos[0]/FrameSize[0], CenterPos[1]/FrameSize[1])
    
    Size = (round(Size[0], 3), round(Size[1], 3))
    Pos = (round(Pos[0], 3), round(Pos[1], 3))
    Ratio = round(ObjectSize[0]/ObjectSize[1], 3)
    print("Valeurs :", str(Pos) + ", " + str(Size) + ", " + str(AnchorPoint) + ", " + str(Ratio))

def DEBUG_SortDishListAlphabetically(DishList):
    if not DEBUG_MODE:
        Warn("SortDishListAlphabetically can't be used")
        return
    
    DishList.sort(key=lambda x: x["Name"].upper())
    return DishList
    
def DEBUG_Hang(sec):
    if not DEBUG_MODE:
        Warn("Hang can't be used")
        return
    
    Warn("Hanging process")
    time.sleep(sec)
    
def DEBUG_PrintStack():
    if not DEBUG_MODE:
        Warn("PrintStack can't be used")
        return
    
    traceback.print_stack()
    
def DEBUG_APICrash():
    if not DEBUG_MODE:
        Warn("APICrash can't be used")
        return
    
    global APIUrl
    APIUrl = "https://10.255.255.1"
    
def DEBUG_Log(Message):
    if not DEBUG_MODE:
        Warn("Log can't be used")
        return
    
    QTimer.singleShot(0, lambda : ThrowFunction(Message))
    
    def ThrowFunction(Message):
        MessageBox = QMessageBox()
        MessageBox.setWindowTitle("DEBUG MESSAGE")
        MessageBox.setText(f"""<p style='text-align: center;'><img src=':/Images/Warning.png' alt='' width='100' height='100'></p>
                              <p style='text-align: center;'>DEBUG MESSAGE</p>
                              <p style='text-align: center;'>{Message}</p>""")
        OkButton = MessageBox.addButton('Ok', QMessageBox.YesRole)
        StyleSheet = MessageStyleSheet(MessageBox)

        OkButton.setStyleSheet(StyleSheet)

        return MessageBox.exec()
    
class OverrideFocus(QObject):    
    def eventFilter(self, Object, Event):
        if KeyOverride and Event.type() == QEvent.KeyPress and Event.key() in [Qt.Key_Tab, Qt.Key_Up, Qt.Key_Down, Qt.Key_Left, Qt.Key_Right, Qt.Key_Return, Qt.Key_Space]:
                KeyHandled = KeyOverrideFunc(Event)
                return KeyHandled
        
        return False
        
class NewSignal(QObject):
    Signal = pyqtSignal()
    
    def Fire(self):
        self.Signal.emit()
        
    def Connect(self, Func):
        self.Signal.connect(Func)

#%% General functions
class MainWindow(QMainWindow): 
    def __init__(self):
        super(MainWindow, self).__init__()
        MainMenuWindow = QMainWindow()
        ChooseMenuWindow = QMainWindow()
        CreateDishWindow = QMainWindow()
        ModifyMenuWindow = QMainWindow()
        SettingsMenuWindow = QMainWindow()
        
        MainMenu = MainMenuModule()
        MainMenu.setupUi(MainMenuWindow)
        ChooseMenu = ChooseMenuModule()
        ChooseMenu.setupUi(ChooseMenuWindow)
        CreateMenu = CreateDishModule()
        CreateMenu.setupUi(CreateDishWindow)
        ModifyMenu = ModifyMenuModule()
        ModifyMenu.setupUi(ModifyMenuWindow)
        SettingsMenu = SettingsMenuModule()
        SettingsMenu.setupUi(SettingsMenuWindow)
        
        self.setWindowTitle("Plat de la Semaine " + AppVersion)
        self.StackedWidget = QStackedWidget()
        self.setCentralWidget(self.StackedWidget)
        self.resizeEvent = self.ResizeEvent
        
        self.Settings = QSettings("Mathecorp", "PlatdelaSemaine")
        if self.Settings.value("DishList") == None:
            self.Settings.setValue("DishList", [])
        if self.Settings.value("DishBackup") == None:
            self.Settings.setValue("DishBackup", {})
        if self.Settings.value("LastVersion") == None:
            self.Settings.setValue("LastVersion", AppVersion)
        if self.Settings.value("ExpectedVersion") == None:
            self.Settings.setValue("ExpectedVersion", AppVersion)
        if self.Settings.value("WindowSize") == None:
            self.Settings.setValue("WindowSize", (868, screen.availableSize().height())) #MainFrame: (850, 750)
        if self.Settings.value("WindowPos") == None:
            self.Settings.setValue("WindowPos", (0, 0))

        self.MainMenu = MainMenu.centralwidget.findChild(QWidget, "MainFrame")
        self.ChooseMenu = ChooseMenu.centralwidget.findChild(QWidget, "MainFrame")
        self.CreateMenu = CreateMenu.centralwidget.findChild(QWidget, "MainFrame")
        self.ModifyMenu = ModifyMenu.centralwidget.findChild(QWidget, "MainFrame")
        self.SettingsMenu = SettingsMenu.centralwidget.findChild(QWidget, "MainFrame")
        
        self.MainMenuNeverActivated = True
        self.ChooseMenuNeverActivated = True
        self.CreateMenuNeverActivated = True
        self.ModifyMenuNeverActivated = True
        self.SettingsMenuNeverActivated = True

        self.StackedWidget.addWidget(self.MainMenu)
        self.StackedWidget.addWidget(self.ChooseMenu)
        self.StackedWidget.addWidget(self.CreateMenu)
        self.StackedWidget.addWidget(self.ModifyMenu)
        self.StackedWidget.addWidget(self.SettingsMenu)

        self.LoadMainMenu()
        WindowSizeX, WindowSizeY = self.Settings.value("WindowSize")
        WindowPosX, WindowPosY = self.Settings.value("WindowPos")
        self.resize(WindowSizeX, WindowSizeY)
        self.move(WindowPosX, WindowPosY)
        self.setMinimumSize(752, 571) #MainFrame: (734, 553)
        self.RetreiveAPIData()
        
    def StartLoading(self, OldWidgets, NewLoader):
        global Loading
        if Loading == True:
            return
        Loading = True    
        
        FadeController = RowFadeController(OldWidgets)
        self.FadeControllers = FadeController
        FadeController.toggle(True, NewLoader)
            
    def EndLoading(self, NewWidgets):
        EndedSignal = NewSignal()
        def OnFadeInEnded():
            global Loading
            Loading = False
            EndedSignal.Fire()
        
        FadeController = RowFadeController(NewWidgets)
        self.FadeControllers = FadeController
        FadeController.toggle(False, OnFadeInEnded)
        return EndedSignal
    
    def ReloadWindow(self):
        WindowSize = QSize(self.width(), self.height())
        self.resizeEvent(QResizeEvent(WindowSize, WindowSize))
        
    def HandleAPIData(self, Reply):
        global RequestSuccessful, FeedbackURL, LatestVersion, DownloadFolder, UpdateDescription
        
        Error = Reply.error()
        if Error == QNetworkReply.NoError:
            AnswerJson = str(Reply.readAll(), "utf-8")
            Answer = json.loads(AnswerJson)[0]
            
            FeedbackURL = Answer["feedback-url"]
            LatestVersion = Answer["latest-version"]
            DownloadFolder = Answer["download-folder"]
            UpdateDescription = Answer["update-description"]
            RequestSuccessful = True
        else:
            RequestSuccessful = False
            Warn("Failed to retreive data")
     
    def RetreiveAPIData(self):
        self.Request = QNetworkRequest(QUrl(APIUrl))
        self.Request.setTransferTimeout(5000)
        self.NetworkManager = QNetworkAccessManager()
        self.NetworkManager.finished.connect(self.HandleAPIData)
        self.NetworkManager.get(self.Request)
        
    def CreateDishListBackup(self, DishList):
        BackupList = self.Settings.value("DishBackup") or {}
        Timestamp = int(time.time())
        while len(BackupList) >= 5:
            OlderTimestamp = min(list(BackupList.keys()))
            del BackupList[OlderTimestamp]
        
        BackupList[Timestamp] = DishList
        self.Settings.setValue("DishBackup", BackupList)
        
    def UpdateDishList(self, NewDishList):
        OldDishList = self.Settings.value("DishList")
        self.CreateDishListBackup(OldDishList)
        self.Settings.setValue("DishList", NewDishList)
        
    def SetFixedSize(self, FontSizeWidgets):
        for WidgetFont in FontSizeWidgets:
            Widget, FontSize = WidgetFont
            Font = Widget.font()
            Font.setPixelSize(FontSize)
            Widget.setFont(Font)
        
    def ScaleFont(self, WidgetList):
        Warn("ScaleFont is deprecated")
        return
        for Widget in WidgetList:
            Font = Widget.font()
        #    Font.setPointSize(round(Font.pointSize() * FontScaleFactor))
            Widget.setFont(Font)
            
    def NoCloseEvent(self, Event):
        WindowSizeX, WindowSizeY = self.width(), self.height()
        WindowPosX, WindowPosY = self.x(), self.y()
        self.Settings.setValue("WindowSize", (WindowSizeX, WindowSizeY))
        self.Settings.setValue("WindowPos", (WindowPosX, WindowPosY))
        
    def DEBUG_SampleDishList(self):
        if not DEBUG_MODE:
            Warn("SampleDishList can't be used")
            return
        
        NewDishList = [{'Name': "Mont d'or", 'Type': 1, 'Season': [0, 1, 2], 'Desc': ""}, {'Name': 'Salade de riz', 'Type': 1, 'Season': [0, 1, 2, 3], 'Desc': "Mettre de l'huile d'olive à couvert et de la pâte brisée."}, {'Name': 'Gratin de pommes de terre et brocolis', 'Type': 1, 'Season': [0, 1, 3], 'Desc': 'Mettre de la crème et du compté.'}, {'Name': 'Tarte aux poireaux', 'Type': 1, 'Season': [1, 2, 3], 'Desc': "Mettre de l'huile d'olive à couvert et de la pâte brisée."}, {'Name': 'Poisson lait de coco et morilles', 'Type': 1, 'Season': [0, 1, 3], 'Desc': 'Mettre de la crème et du compté.'}, {'Name': 'Lentilles', 'Type': 1, 'Season': [0], 'Desc': "Mettre 3 volumes d'eau pour un volume de lentilles. Si le plat est chaud, mettre du bouillon, de l'oignon ou de l'ai, du curry... pendant 20 minutes"}, {'Name': 'Purée maison', 'Type': 1, 'Season': [2], 'Desc': 'Eplucher les pommes de terre, laver les PDT, faire chauffer l’eau et lait, mettre les PDT dans la casserole avec l’eau et le lait, les mettre dans un saladier avec grande une cuillère d’eau et de lait, écraser les PDT les unes après les autres, rajouter du lait, du sel et du beurre et enfin mélanger.'}, {'Name': 'Salade de courgettes', 'Type': 1, 'Season': [0, 1, 2, 3], 'Desc': "Pour la sauce, mettre de l'huile d'olive, du jus de citron, du sel et du poivre."}, {'Name': 'Tranches d’aubergines', 'Type': 1, 'Season': [0, 1, 3], 'Desc': "Refaire venir les tranches d'aubergine avec de l'huile d'olive à l'ail et du sel"}, {'Name': 'Pâtes de riz, menthe, salade, sauce pour nems et viande', 'Type': 1, 'Season': [2, 3], 'Desc': 'La viande peut être du poulet ou du canard'}, {'Name': "Gigot d'agneau, semoule et raisins", 'Type': 1, 'Season': [0, 2, 3], 'Desc': "Marinade de 2cl d'huile olive, 1cl de sauce soja et 1c d’ail moulu. Pour la semoule pendant ce temps : faire revenir les raisins dans le beurre pour les chauffer et faire cuire la semoule puis faire chauffer la semoule dans le beurre et les raisons de la poêle. La poêle doit être sur 9 avec du beurre, faire dorer la viande des 2 cotés très rapidement (1 a 2 mn) en mettant le reste de marinade en bougeant toujours la viande en appuyant sur le gras. Continuer à cuire encore un peu fort 2/3mn de chaque côté, puis baisser à 5 ou 6. Quand c’est cuit, déglacer avec eau, sauce soja puis ajouter ail sans le cuire"}, {'Name': 'Salade vermicelle de riz', 'Type': 1, 'Season': [0, 1], 'Desc': "Commencez par faire cuire les vermicelles en les mettant dans un saladier, recouvrez-les d'eau bouillante et laissez gonfler 10 minutes. Décortiquez les crevettes si besoin, découpez en dés les avocats. Pressez le citron vert. Dans un autre saladier mélangez 3 CS d'huile d'olive, 1 CS de jus de citron, 1 CS de nuoc mam, et 2 CS de sauce soja. Égouttez les vermicelles, rincez-les à l'eau froide, égouttez-les de nouveau puis mélangez-les à la sauce et ajoutez les crevettes et dés d'avocat. Ciselez la coriandre et ajoutez-la. Ajustez l'assaisonnement selon vos goûts et c'est prêt"}, {'Name': 'Lentilles, tomates et champignons', 'Type': 1, 'Season': [0, 1, 2, 3], 'Desc': 'Premièrement, versez vos lentilles dans un plat et ajoutez-y de l\'eau. Rincez les plusieurs fois, puis une fois que l\'eau de trempage est un peu moins trouble, réservez-les, tout en les laissant dans l\'eau. Coupez votre oignon, puis faites le revenir dans un fait-tout avec un peu d\'huile d\'olive. Le but est de le faire fondre un peu. Ajoutez ensuite vos champignons et votre tomate. (Si vous utilisez du concentré de tomate, vous le rajouterez en fin de cuisson). Une fois que ces légumes sont un peu "grillés", égouttez les lentilles, et ajoutez-les dans le fait-tout pour les faire revenir quelques minutes. Ajoutez ensuite deux verres d\'eau, couvrez et baissez le feu. Remuez de temps en temps, et rajoutez de l\'eau si nécessaire, à la façon d\'un risotto. Vous maîtriserez ainsi la cuisson de vos lentilles. Après environ 8 minutes de cuissons, vos lentilles seront cuites ! Il est temps de rajouter le concentré de tomates pour ceux qui n\'ont pas mis de tomate au début.'}, {'Name': 'Champignons au four', 'Type': 1, 'Season': [0, 1, 2, 3], 'Desc': 'Mettre les champignons entiers sur la tête au moins 30 mn à 180 jusqu’à ce qu’ils suent des pieds. Une variante est de mettre du fromage type boursin à la place du pied au raz de la tête. Je les émince et j’ajoute huile et ail comme ta recette de poivrons. Il faut laisser reposer.'}, {'Name': 'Bo bun', 'Type': 1, 'Season': [0, 1, 2, 3], 'Desc': 'Le Bo bun est encore meilleur avec de la "Sauce nuoc mam pour nems" !'}, {'Name': 'Tagliatelles au saumon', 'Type': 1, 'Season': [0, 1, 2, 3], 'Desc': "ÉTAPE 1 : Cuire les pâtes à l'eau bouillante salée selon le temps indiqué sur le paquet. ÉTAPE 2 : Pendant ce temps, faire fondre le beurre dans une casserole et y ajouter la crème. ÉTAPE 3 : Quand la crème est bien chaude, y plonger les dés de saumon, ils doivent cuire à la chaleur de la crème. ÉTAPE 4 : Quand ils sont cuits (ils doivent se détacher), ajouter le sel, le poivre et la muscade moulue. ÉTAPE 5 : Égoutter les pâtes, les disposer dans un grand plat rond et napper de crème au saumon. ÉTAPE 6 : Servir avec du parmesan."}, {"Name": "Soupe de Potiron", "Type": 0, "Season": [2, 3], "Desc": "Une soupe chaude et réconfortante à base de potiron, parfaite pour l'automne et l'hiver."}, {"Name": "Salade Niçoise", "Type": 0, "Season": [1], "Desc": "Une salade estivale avec des légumes frais, du thon, des œufs et des olives."}, {"Name": "Tarte aux Pommes", "Type": 2, "Season": [2, 3], "Desc": "Une tarte classique avec des pommes caramélisées, idéale pour les saisons plus fraîches."}, {"Name": "Gratin Dauphinois", "Type": 1, "Season": [2, 3], "Desc": "Un plat réconfortant de pommes de terre cuites à la crème, idéal pour l'automne et l'hiver."}, {"Name": "Crème Brûlée", "Type": 2, "Season": [3, 0], "Desc": "Un dessert crémeux avec une croûte de sucre caramélisé, parfait en toute saison."}, {"Name": "Bouillabaisse", "Type": 1, "Season": [1], "Desc": "Une soupe de poisson provençale riche en saveurs, idéale pour l'été."}, {"Name": "Salade de Lentilles", "Type": 0, "Season": [0, 2], "Desc": "Une salade fraîche et nourrissante, parfaite pour le printemps et l'automne."}, {"Name": "Coq au Vin", "Type": 1, "Season": [2, 3], "Desc": "Un classique français avec du poulet mijoté au vin rouge, parfait pour l'automne et l'hiver."}, {"Name": "Mousse au Chocolat", "Type": 2, "Season": [0, 3], "Desc": "Un dessert aérien et riche en chocolat, apprécié en toute saison."}, {"Name": "Ratatouille", "Type": 1, "Season": [1], "Desc": "Un plat de légumes provençal, idéal pour l'été."}, {"Name": "Escargots à la Bourguignonne", "Type": 0, "Season": [3], "Desc": "Des escargots cuits dans une sauce au beurre et à l'ail, parfaits pour l'hiver."}, {"Name": "Galette des Rois", "Type": 2, "Season": [3], "Desc": "Un dessert traditionnel de l'Épiphanie avec une pâte feuilletée et une frangipane."}, {"Name": "Quiche Lorraine", "Type": 1, "Season": [0, 2], "Desc": "Une tarte salée à base de crème, d'œufs et de lardons, parfaite pour le printemps et l'automne."}, {"Name": "Soupe à l'Oignon", "Type": 0, "Season": [3], "Desc": "Une soupe classique avec des oignons caramélisés, gratinée avec du fromage, idéale pour l'hiver."}, {"Name": "Profiteroles", "Type": 2, "Season": [0, 3], "Desc": "Un dessert composé de choux garnis de crème glacée et nappés de chocolat fondu."}, {"Name": "Bouef Bourguignon", "Type": 1, "Season": [2, 3], "Desc": "Un ragoût de bœuf mijoté au vin rouge, parfait pour l'automne et l'hiver."}, {"Name": "Salade de Chèvre Chaud", "Type": 0, "Season": [0, 1], "Desc": "Une salade avec du fromage de chèvre fondu sur du pain grillé, idéale pour le printemps et l'été."}, {"Name": "Tarte Tatin", "Type": 2, "Season": [2, 3], "Desc": "Une tarte renversée avec des pommes caramélisées, idéale pour l'automne et l'hiver."}, {"Name": "Foie Gras", "Type": 0, "Season": [3], "Desc": "Un foie gras délicatement assaisonné, servi en entrée pour les occasions spéciales."}, {"Name": "Cassoulet", "Type": 1, "Season": [2, 3], "Desc": "Un plat copieux à base de haricots blancs, de saucisses et de confit de canard, idéal pour l'automne et l'hiver."}, {"Name": "Crêpes Suzette", "Type": 2, "Season": [0, 1], "Desc": "Des crêpes fines servies avec une sauce à l'orange et flambées au Grand Marnier."}, {"Name": "Salade de Fruits d'Été", "Type": 2, "Season": [1], "Desc": "Une salade rafraîchissante de fruits frais, parfaite pour l'été."}, {"Name": "Tartiflette", "Type": 1, "Season": [2, 3], "Desc": "Un plat savoyard à base de pommes de terre, de lardons et de reblochon, parfait pour l'hiver."}, {"Name": "Pot-au-Feu", "Type": 1, "Season": [2, 3], "Desc": "Un ragoût de bœuf et de légumes mijoté, idéal pour l'automne et l'hiver."}, {"Name": "Soufflé au Fromage", "Type": 0, "Season": [0, 2], "Desc": "Un soufflé léger et aérien au fromage, parfait en entrée."}, {"Name": "Gâteau au Chocolat", "Type": 2, "Season": [0, 3], "Desc": "Un gâteau riche en chocolat, parfait en toute saison."}, {"Name": "Risotto aux Champignons", "Type": 1, "Season": [2, 3], "Desc": "Un risotto crémeux avec des champignons, idéal pour l'automne et l'hiver."}, {"Name": "Baba au Rhum", "Type": 2, "Season": [0, 3], "Desc": "Un gâteau moelleux imbibé de rhum et servi avec de la crème fouettée."}, {"Name": "Salade de Fenouil", "Type": 0, "Season": [0, 1], "Desc": "Une salade croquante et rafraîchissante, parfaite pour le printemps et l'été."}, {"Name": "Tarte aux Fraises", "Type": 2, "Season": [0, 1], "Desc": "Une tarte garnie de fraises fraîches, idéale pour le printemps et l'été."}, {"Name": "Omelette aux Truffes", "Type": 0, "Season": [2, 3], "Desc": "Une omelette parfumée aux truffes, parfaite pour l'automne et l'hiver."}, {"Name": "Soupe de Carottes au Gingembre", "Type": 0, "Season": [0, 2], "Desc": "Une soupe réconfortante avec des carottes et du gingembre, idéale pour le printemps et l'automne."}, {"Name": "Fondue Savoyarde", "Type": 1, "Season": [3], "Desc": "Une fondue au fromage, parfaite pour les soirées d'hiver."}, {"Name": "Clafoutis aux Cerises", "Type": 2, "Season": [0, 1], "Desc": "Un dessert moelleux aux cerises, idéal pour le printemps et l'été."}, {"Name": "Rillettes de Poisson", "Type": 0, "Season": [0, 1], "Desc": "Une entrée fraîche à base de poisson, parfaite pour le printemps et l'été."}, {"Name": "Poulet Basquaise", "Type": 1, "Season": [1, 2], "Desc": "Un plat de poulet mijoté avec des poivrons et des tomates, idéal pour l'été et l'automne."}, {"Name": "Paris-Brest", "Type": 2, "Season": [0, 3], "Desc": "Un dessert en forme de couronne, garni de crème pralinée, apprécié en toute saison."}, {"Name": "Salade de Betteraves", "Type": 0, "Season": [0, 2], "Desc": "Une salade colorée et nourrissante, parfaite pour le printemps et l'automne."}, {"Name": "Rôti de Porc aux Pruneaux", "Type": 1, "Season": [2, 3], "Desc": "Un rôti de porc sucré-salé, idéal pour l'automne et l'hiver."}, {"Name": "Tarte au Citron Meringuée", "Type": 2, "Season": [0, 1], "Desc": "Une tarte au citron garnie de meringue, idéale pour le printemps et l'été."}, {"Name": "Poisson en Croûte de Sel", "Type": 1, "Season": [1], "Desc": "Un poisson cuit en croûte de sel, parfait pour l'été."}, {"Name": "Salade Waldorf", "Type": 0, "Season": [0, 1], "Desc": "Une salade croquante avec des pommes, des noix et du céleri, parfaite pour le printemps et l'été."}, {"Name": "Sole Meunière", "Type": 1, "Season": [1], "Desc": "Un poisson cuit à la poêle avec du beurre, idéal pour l'été."}, {"Name": "Gâteau de Riz", "Type": 2, "Season": [2, 3], "Desc": "Un dessert traditionnel à base de riz au lait, parfait pour l'automne et l'hiver."}, {"Name": "Soupe Minestrone", "Type": 0, "Season": [0, 2], "Desc": "Une soupe italienne pleine de légumes, idéale pour le printemps et l'automne."}, {"Name": "Bœuf Stroganoff", "Type": 1, "Season": [2, 3], "Desc": "Un plat de bœuf crémeux avec des champignons, idéal pour l'automne et l'hiver."}, {"Name": "Salade de Courgettes", "Type": 0, "Season": [0, 1], "Desc": "Une salade légère de courgettes marinées, parfaite pour le printemps et l'été."}, {"Name": "Gâteau aux Noix", "Type": 2, "Season": [2, 3], "Desc": "Un gâteau moelleux aux noix, idéal pour l'automne et l'hiver."}, {"Name": "Blanquette de Veau", "Type": 1, "Season": [2, 3], "Desc": "Un ragoût de veau crémeux, parfait pour l'automne et l'hiver."}, {"Name": "Crêpes de Sarrasin", "Type": 1, "Season": [0, 1], "Desc": "Des crêpes salées faites avec de la farine de sarrasin, idéales pour le printemps et l'été."}]
        self.UpdateDishList(DEBUG_SortDishListAlphabetically(NewDishList))

    def DEBUG_TinyDishList(self):
        if not DEBUG_MODE:
            Warn("TinyDishList can't be used")
            return
        
        NewDishList = [{'Name': "Mont d'or", 'Type': 1, 'Season': [0, 1, 2], 'Desc': ""}, {'Name': 'Salade de riz', 'Type': 1, 'Season': [0, 1, 2, 3], 'Desc': "Mettre de l'huile d'olive à couvert et de la pâte brisée."}, {'Name': 'Gratin de pommes de terre et brocolis', 'Type': 1, 'Season': [0, 1, 3], 'Desc': 'Mettre de la crème et du compté.'}, {'Name': 'Tarte aux poireaux', 'Type': 1, 'Season': [1, 2, 3], 'Desc': "Mettre de l'huile d'olive à couvert et de la pâte brisée."}, {'Name': 'Poisson lait de coco et morilles', 'Type': 1, 'Season': [0, 1, 3], 'Desc': 'Mettre de la crème et du compté.'}]
        self.UpdateDishList(DEBUG_SortDishListAlphabetically(NewDishList))
        
    def DEBUG_EraseAllData(self):
        if not DEBUG_MODE:
            Warn("EraseAllData can't be used")
            return
        
        self.Settings.setValue("DishList", [])
        self.Settings.setValue("DishBackup", {})
        

#%% MainMenu
    def LoadMainMenu(self):
        global FirstStart, ImpactedWidgetDisplay, CustomResizeFunctions, KeyOverride
        ImpactedWidgetDisplay = []
        CustomResizeFunctions = []
        KeyOverride = False
        
        self.StackedWidget.setCurrentIndex(0)
    
        self.MenusImage = self.findChild(QWidget, "MenusImage")
        self.MenusText = self.findChild(QWidget, "MenusText")
        self.AddImage = self.findChild(QWidget, "AddImage")
        self.AddText = self.findChild(QWidget, "AddText")
        self.ModifyImage = self.findChild(QWidget, "ModifyImage")
        self.ModifyText = self.findChild(QWidget, "ModifyText")
        self.SettingsImage = self.findChild(QWidget, "SettingsImage")
        self.SettingsText = self.findChild(QWidget, "SettingsText")
        self.Logo = self.findChild(QWidget, "Logo")
        
        #AddWidgetDisplayInfo(self.MenusImage, (0.480, 0.576), (0.304, 0.269), (1, 1), 1.277)
        #AddWidgetDisplayInfo(self.AddImage, (0.529, 0.576), (0.304, 0.269), (0, 1), 1.277)
        #AddWidgetDisplayInfo(self.ModifyImage, (0.480, 0.613), (0.304, 0.269), (1, 0), 1.277)
        #AddWidgetDisplayInfo(self.SettingsImage, (0.529, 0.613), (0.304, 0.269), (0, 0), 1.277)
        
        #AddWidgetDisplayInfo(self.Logo, (0.500, 0.133), (0.588, 0.267), (0.5, 0.5), 2.500)

        self.ResizeWidget = QWidget()
        AddWidgetDisplayInfo(self.ResizeWidget, (0.5, 0.0), (0.965, 0.985), (0.5, 0), 0.824, 700)
        
        self.MenusImage.mousePressEvent = self.ChooseMenuClicked
        self.MenusText.mousePressEvent = self.ChooseMenuClicked
        self.AddImage.mousePressEvent = self.CreateMenuClicked
        self.AddText.mousePressEvent = self.CreateMenuClicked
        self.ModifyImage.mousePressEvent = self.ModifyMenuClicked
        self.ModifyText.mousePressEvent = self.ModifyMenuClicked
        self.SettingsImage.mousePressEvent = self.SettingsMenuClicked
        self.SettingsText.mousePressEvent = self.SettingsMenuClicked
        self.closeEvent = self.NoCloseEvent

        ImpactedWidgetDisplay = [self.ResizeWidget]
        CustomResizeFunctions = [self.ResizeMainMenu]
        self.MainMenuWidgetList = [self.MenusImage, self.MenusText, self.AddImage, self.AddText, self.ModifyImage, self.ModifyText, self.SettingsImage, self.SettingsText, self.Logo]
        
        self.ReloadWindow()
        self.MainMenuNeverActivated = False
        
        if Version(AppVersion) < Version(self.Settings.value("ExpectedVersion")) and FirstStart and not NO_UPDATE_ERROR:
            QTimer.singleShot(0, self.UpdateError)
            self.Settings.setValue("ExpectedVersion", AppVersion)
        
        if FirstStart:
            FirstStart = False
        else:
            self.EndLoading(self.MainMenuWidgetList)
     
    def ChooseMenuClicked(self, Event):
        self.StartLoading(self.MainMenuWidgetList, self.LoadChooseMenu)
        
    def CreateMenuClicked(self, Event):
        self.StartLoading(self.MainMenuWidgetList, self.LoadCreateDish)

    def ModifyMenuClicked(self, Event):
        self.StartLoading(self.MainMenuWidgetList, self.LoadModifyMenu)

    def SettingsMenuClicked(self, Event):
        self.StartLoading(self.MainMenuWidgetList, self.LoadSettingsMenu)

    def ResizeMainMenu(self, NewSize):
        ResizeWidgetSizeX = self.ResizeWidget.width()
        ResizeWidgetSizeY = self.ResizeWidget.height()
        ResizeWidgetPosX = self.ResizeWidget.x()
    
        LogoSizeX = int(0.894 * ResizeWidgetSizeX)
        LogoSizeY = int(0.302 * ResizeWidgetSizeY)
        LogoPosX = int(ResizeWidgetPosX + (ResizeWidgetSizeX - LogoSizeX)/2)
        LogoPosY = int(0)      
        self.Logo.setGeometry(LogoPosX, LogoPosY, LogoSizeX, LogoSizeY)
        
        MenusSizeX = int(0.460 * ResizeWidgetSizeX)
        MenusSizeY = int(0.298 * ResizeWidgetSizeY)
        MenusPosX = int(ResizeWidgetPosX)
        MenusPosY = int(0.342 * ResizeWidgetSizeY) 
        self.MenusImage.setGeometry(MenusPosX, MenusPosY, MenusSizeX, MenusSizeY)
        
        MenusTextSizeX = int(0.711 * MenusSizeX)
        MenusTextSizeY = int(0.154 * MenusSizeY)
        MenusTextPosX = int(MenusPosX + MenusSizeX/2 - MenusTextSizeX/2)
        MenusTextPosY = int(MenusPosY + 0.692 * MenusSizeY)
        self.MenusText.setGeometry(MenusTextPosX, MenusTextPosY, MenusTextSizeX, MenusTextSizeY)
        
        MenusFont = self.MenusText.font()
        MenusFont.setPixelSize(int(0.613 * MenusTextSizeY))
        self.MenusText.setFont(MenusFont)
        
        AddSizeX = MenusSizeX
        AddSizeY = MenusSizeY
        AddPosX = int(ResizeWidgetPosX + ResizeWidgetSizeX - AddSizeX)
        AddPosY = MenusPosY
        self.AddImage.setGeometry(AddPosX, AddPosY, AddSizeX, AddSizeY)
        
        AddTextSizeX = MenusTextSizeX
        AddTextSizeY = MenusTextSizeY
        AddTextPosX = int(AddPosX + AddSizeX/2 - AddTextSizeX/2)
        AddTextPosY = MenusTextPosY
        self.AddText.setGeometry(AddTextPosX, AddTextPosY, AddTextSizeX, AddTextSizeY)
        self.AddText.setFont(MenusFont)
        
        ModifySizeX = MenusSizeX
        ModifySizeY = MenusSizeY
        ModifyPosX = MenusPosX
        ModifyPosY = int(ResizeWidgetSizeY - ModifySizeY)
        self.ModifyImage.setGeometry(ModifyPosX, ModifyPosY, ModifySizeX, ModifySizeY)
        
        ModifyTextSizeX = MenusTextSizeX
        ModifyTextSizeY = MenusTextSizeY
        ModifyTextPosX = MenusTextPosX
        ModifyTextPosY = int(ModifyPosY + 0.692 * ModifySizeY)
        self.ModifyText.setGeometry(ModifyTextPosX, ModifyTextPosY, ModifyTextSizeX, ModifyTextSizeY)
        self.ModifyText.setFont(MenusFont)
        
        SettingSizeX = MenusSizeX
        SettingsSizeY = MenusSizeY
        SettingsPosX = AddPosX
        SettingsPosY = ModifyPosY
        self.SettingsImage.setGeometry(SettingsPosX, SettingsPosY, SettingSizeX, SettingsSizeY)
        
        SettingsTextSizeX = MenusTextSizeX
        SettingsTextSizeY = MenusTextSizeY
        SettingsTextPosX = AddTextPosX
        SettingsTextPosY = ModifyTextPosY
        self.SettingsText.setGeometry(SettingsTextPosX, SettingsTextPosY, SettingsTextSizeX, SettingsTextSizeY)
        self.SettingsText.setFont(MenusFont)
        
    def UpdateError(self):
        MessageBox = QMessageBox()
        MessageBox.setWindowTitle("Attention")
        MessageBox.setText("""<p style='text-align: center;'><img src=':/Images/Warning.png' alt='' width='100' height='100'></p>
                               <p style='text-align: center;'>La dernière mise à jour semble avoir échouée</p>
                               <p style='text-align: center;'>Si le problème persiste, réinstallez manuellement l'application</p>""")
        ReinstallButton = MessageBox.addButton("Réinstaller l'application", QMessageBox.YesRole)
        IgnoreButton = MessageBox.addButton('Ignorer', QMessageBox.RejectRole)
        StyleSheet = MessageStyleSheet(MessageBox)

        ReinstallButton.setStyleSheet(StyleSheet)
        IgnoreButton.setStyleSheet(StyleSheet)

        Answer = MessageBox.exec()

        if Answer == 1:
            return
        
        webbrowser.open(DownloadFolder)
        self.closeEvent = self.NoCloseEvent
        self.close()

#%% ChooseMenu           
    def LoadChooseMenu(self):
        global ImpactedWidgetDisplay, CustomResizeFunctions, KeyOverride, KeyOverrideFunc
        ImpactedWidgetDisplay = []
        CustomResizeFunctions = []
        KeyOverride = True
        KeyOverrideFunc = self.ChooseKeyPressEvent
        
        self.StackedWidget.setCurrentIndex(1)
            
        self.ScrollArea = self.findChild(QWidget, "ScrollArea")
        self.ScrollContent = self.findChild(QWidget, "ScrollAreaWidgetContents")
        self.Transition1 = self.findChild(QWidget, "Transition1")
        self.Transition2 = self.findChild(QWidget, "Transition2")
        self.AcceptButton = self.findChild(QWidget, "AcceptButton")
        self.RefuseButton = self.findChild(QWidget, "RefuseButton")
        self.UndoButton = self.findChild(QWidget, "UndoButton")
        self.UndoText = self.findChild(QWidget, "UndoText")
        self.EndButton = self.findChild(QWidget, "EndButton")
        self.EndText = self.findChild(QWidget, "EndText")
        self.BackChoiceButton = self.findChild(QWidget, "BackChoiceButton")
        self.BackChoiceText = self.findChild(QWidget, "BackChoiceText")
        self.UpdateButton = self.findChild(QWidget, "UpdateButton")
        self.UpdateText = self.findChild(QWidget, "UpdateText")
        self.CountFrame = self.findChild(QWidget, "CountFrame")
        self.StarterCountWidget = self.findChild(QWidget, "StarterCount")
        self.DishCountWidget = self.findChild(QWidget, "DishCount")
        self.DessertCountWidget = self.findChild(QWidget, "DessertCount")
        self.LeaveChooseButton = self.findChild(QWidget, "LeaveChoose")
        
        self.Transition1.hide()
        self.Transition2.hide()
        self.CurrentlyAnimating = False
        self.EndMode = False
        self.StopAllAnim = False
        self.AnimIgnoreNextResize = False
        self.ReverseDish = None
        self.CurrentDish = QWidget()
        self.ScrollWidget = QWidget()
        self.HorizontalScrollBar = self.ScrollArea.horizontalScrollBar()
        self.VerticalScrollBar = self.ScrollArea.verticalScrollBar()
        self.BackChoiceButton.setVisible(False)
        self.BackChoiceText.setVisible(False)
        self.UpdateButton.setVisible(False)
        self.UpdateText.setVisible(False)
        
        self.ScrollVBox = QVBoxLayout(self.ScrollWidget)
        self.ScrollVBox.setAlignment(Qt.AlignTop)
        self.ScrollAnim = QPropertyAnimation(self.ScrollArea, b"pos")
        self.ScrollAnim.setEndValue(QPoint(0,0))
        self.DishPosAnim = QPropertyAnimation(self.CurrentDish, b"pos")
        self.DishPosAnim.setEndValue(QPoint(0,0))
        self.DishSizeAnim = QPropertyAnimation(self.CurrentDish, b"size")
        self.DishSizeAnim.setEndValue(QSize(0,0))
        self.QWidgetList = []
        self.DishList = []
        self.ReverseCache = []
        self.ActionHistory = []
        self.DishListState = 0
        self.StarterCount = 0
        self.DishCount = 0
        self.DessertCount = 0
        self.HorizontalScrollBar.setEnabled(False)
        self.VerticalScrollBar.setEnabled(False)
        self.ScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.ScrollArea.setWidget(self.ScrollWidget)
        self.ScrollArea.setWidgetResizable(True)
        self.AcceptButton.setEnabled(True)
        self.RefuseButton.setEnabled(True)
        self.UndoButton.setEnabled(False)
        self.UndoText.setEnabled(False)
        self.EndButton.setEnabled(False)
        self.EndText.setEnabled(False)
        self.UndoButton.show()
        self.UndoText.show()
        self.EndButton.show()
        self.EndText.show()
        self.StarterCountWidget.setText("<b>0</b> Entrée")
        self.DishCountWidget.setText("<b>0</b> Plat")
        self.DessertCountWidget.setText("<b>0</b> Dessert")
    
        CustomResizeFunctions = [self.CancelAllAnim,  self.ResizeScroll, self.ResizeScrollItems, self.ResizeForButtons]
        FontSizeWidgets = [(self.StarterCountWidget, 23), (self.DishCountWidget, 23), (self.DessertCountWidget, 23), (self.LeaveChooseButton, 23)]
        self.SetFixedSize(FontSizeWidgets)
        
        self.VerticalScrollBar.valueChanged.connect(self.OnScrolling)
        self.AcceptButton.mousePressEvent = self.AddCurrentDishToScroll
        self.RefuseButton.mousePressEvent = self.RefuseDish
        self.UndoButton.mousePressEvent = self.ReverseChoice
        self.UndoText.mousePressEvent = self.ReverseChoice
        self.EndButton.mousePressEvent = self.EndChoosing
        self.EndText.mousePressEvent = self.EndChoosing
        self.BackChoiceButton.mousePressEvent = self.BackChoiceAnimation
        self.BackChoiceText.mousePressEvent = self.BackChoiceAnimation
        self.UpdateButton.mousePressEvent = self.ShowUpdateConfirm
        self.UpdateText.mousePressEvent = self.ShowUpdateConfirm
        self.LeaveChooseButton.mousePressEvent = self.LeaveChoose
        self.closeEvent = self.ChooseMenuCloseEvent
        
        self.AnimIgnoreNextResize = True
        self.ChooseMenuNeverActivated = False
        self.ReloadWindow()
        self.SummonDish()
        self.EndLoading([])
         
    def GetSeasonString(self, SeasonList):
        SeasonCount = len(SeasonList)
        if SeasonCount == 4:
            return "Toutes saisons"
        
        SeasonStrings = ["Printemps", "Été", "Automne", "Hiver"]
        StringResult = ""
        
        for i, v in enumerate(SeasonList):
            Separator = "" if i == 0 else ", " if i != SeasonCount - 1 else " et "
            StringResult += Separator + SeasonStrings[v]
            
        return StringResult
    
    def ExtractRightSeasons(self, Season):
        DishList = []
        for DishDict in self.Settings.value("DishList"):
            DishSeason = DishDict["Season"]
            if Season in DishSeason or len(DishSeason) == 4:
                DishList.append(DishDict)
        return DishList
    
    def ExtractWrongSeasons(self, Season):
        DishList = []
        for DishDict in self.Settings.value("DishList"):
            DishSeason = DishDict["Season"]
            if Season not in DishSeason and len(DishSeason) != 4:
                DishList.append(DishDict)
        return DishList
        
    def SetDishList(self):
        if len(self.DishList) != 0:
            return
        
        DayElapsed = date.today().timetuple().tm_yday
        if 80 <= DayElapsed < 172:
            Season = 0 #Spring
        elif 172 <= DayElapsed < 264:
            Season = 1 #Summer
        elif 264 <= DayElapsed < 355:
            Season = 2 #Autumn
        else:
            Season = 3 #Winter
        
        if self.DishListState == 0:
            self.DishListState = 1
            DishList = self.ExtractRightSeasons(Season)
        elif self.DishListState == 1:
            self.DishListState = 2
            self.NotEnoughSeasonMessage()
            DishList = self.ExtractWrongSeasons(Season)
        elif self.DishListState == 2:
            self.DishListState = 3
            self.NotEnoughDishMessage()
            DishList = self.ExtractRightSeasons(Season)
        elif self.DishListState == 3:
            self.DishListState = 4
            self.NotEnoughSeasonMessage()
            DishList = self.ExtractWrongSeasons(Season)
        else:
            self.NoDishLeftMessage()
            DishList = [{'Name': 'Aucun plat disponible', 'Desc': 'Aucun plat disponible','Season': [0, 1, 2, 3], 'Type': 1}]
        
        if len(DishList) == 0:
            self.SetDishList()
            return
                
        self.DishList = DishList
    
    def GetCurrentDishPos(self, Dish=None):
        PixelScrolled = self.VerticalScrollBar.value()
        if PixelScrolled > 40:
            PixelScrolled = 40
            
        ScrollPosX = self.ScrollArea.x()
        ScrollPosY = self.ScrollArea.y()
        ScrollSizeX = self.ScrollArea.width()
        
        DescOffset = Dish.height() - 150 if Dish else 0
        
        return (ScrollPosX + ScrollSizeX - 413, ScrollPosY - PixelScrolled - DescOffset - 147)
         
    def CreateDishUi(self, DishName, DishType, DishSeason, DishDesc, ModifyMode=False, DescOpen=False):
        CurrentDishPosX, CurrentDishPosY = self.GetCurrentDishPos()
        Window = self.ModifyMenu if ModifyMode else self.ChooseMenu
        UiModule = SettingsDishModule if ModifyMode else DishModule
        
        CreatedDish = QWidget(Window)
        CreatedDish.setGeometry(CurrentDishPosX, -240, 400, 150)
        
        DishUi = UiModule()
        DishUi.setupUi(CreatedDish)
        CreatedDish.show()
        CreatedDish.lower()

        Name = DishUi.Name
        Type_Season = DishUi.Type_Season
        Description = DishUi.Description
        SeeMore = DishUi.SeeMore
        Separation = DishUi.Separation
        Modify = DishUi.ModifyDishButton if ModifyMode else QWidget()

        Type_Season.setProperty("Type", DishType)
        Type_Season.setProperty("Season", [str(x) for x in DishSeason])
        
        DishType = ["Entrée", "Plat", "Dessert"][DishType]
        DishSeason = self.GetSeasonString(DishSeason)
        DishDesc = DishDesc if DishDesc != "" else "Aucune description"
        
        Description.setProperty("CompleteDesc", DishDesc)
        Separation.hide()

        Desc, DescFit = MakeTextFitByCropping(DishDesc, DishUi.Description, 4, " <b>Voir plus</b>")
        if DescFit == True:
            SeeMore.hide()
        else:
            FontMetrics = QFontMetrics(SeeMore.font())
            SeeMoreTextRect = FontMetrics.tightBoundingRect("Voir plus")
            SeeMore.resize(SeeMoreTextRect.width() + 3, SeeMore.height())
            Description.setProperty("CroppedDesc", Desc)
            
        if ModifyMode == True:
            self.ConnectModifyDish(CreatedDish)
        
        FontSizeWidgets = [(Name, 20), (Type_Season, 13), (Description, 13), (SeeMore, 13), (Modify, 13)]
        self.SetFixedSize(FontSizeWidgets)
        Name.setFont(MakeTextFitWithSize(DishName, Name, 1, 0))
            
        Name.setText(DishName)
        Type_Season.setText(DishType + " • " + DishSeason)
        Description.setText(Desc)
        self.ConnectSeeMore(CreatedDish, DescOpen)
        
        return CreatedDish
   
    def SummonDish(self, NextFunc=lambda:None):
        CurrentDishPosX, CurrentDishPosY = self.GetCurrentDishPos()
        self.CurrentlyAnimating = True

        if len(self.ReverseCache) == 0:
            self.SetDishList()
            DishId = random.randrange(0, len(self.DishList))
            Dish = self.DishList.pop(DishId)
            
            self.CurrentDish = self.CreateDishUi(Dish["Name"], Dish["Type"], Dish["Season"], Dish["Desc"])
        else:
            self.CurrentDish = self.ReverseCache.pop()
            self.CurrentDish.show()
            self.CurrentDish.move(CurrentDishPosX, - 90 - self.CurrentDish.height())
            self.CurrentDish.lower()
        
        def AnimationEnded():
            PixelScrolled = self.VerticalScrollBar.value()
            self.AnimCompleted()
            self.OnScrolling(PixelScrolled)
            self.RemoveGlitches()
            NextFunc()
            
        def AnimationStepped(NewValue):
            if NewValue.y() > - 200:
                self.repaint()

        self.DishPosAnim = QPropertyAnimation(self.CurrentDish, b"pos")
        self.DishPosAnim.setEndValue(QPoint(CurrentDishPosX, CurrentDishPosY - self.CurrentDish.height() + 150))
        self.DishPosAnim.setDuration(600)
        if CompatibilitySize:
            self.DishPosAnim.valueChanged.connect(AnimationStepped)
        
        self.StartAnim(self.DishPosAnim, AnimationEnded)
      
    def ReverseSummonDish(self, NextFunc):
        CurrentDishPosX, CurrentDishPosY = self.GetCurrentDishPos()
        self.CurrentlyAnimating = True
        
        def AnimationEnded():
            self.CurrentDish.hide()
            self.ReverseCache.append(self.CurrentDish)
            NextFunc()

        self.DishPosAnim = QPropertyAnimation(self.CurrentDish, b"pos")
        self.DishPosAnim.setEndValue(QPoint(CurrentDishPosX, - 80 - self.CurrentDish.height()))
        self.DishPosAnim.setDuration(600)

        self.StartAnim(self.DishPosAnim, AnimationEnded)
    
    def AdjustTransition(self, PixelScrolled):
        if PixelScrolled > 15: 
            self.Transition1.show()
            self.Transition1.raise_()
            self.Transition2.show()
            self.Transition1.raise_()
        else:
            self.Transition1.hide()
            self.Transition1.lower()
            self.Transition2.hide()
            self.Transition2.lower()
       
    def OnScrolling(self, PixelScrolled):
        if self.EndMode == True:
            return
        
        if PixelScrolled > 40:
            PixelScrolled = 40
            
        self.AdjustTransition(PixelScrolled)
        
        if self.CurrentlyAnimating == True:
            self.DishPosAnim.setDuration(0)
            self.AnimCompleted()
            
        CurrentDishPosX, CurrentDishPosY = self.GetCurrentDishPos()
        self.CurrentDish.move(CurrentDishPosX, CurrentDishPosY - self.CurrentDish.height() + 150)
            
    def CancelAllAnim(self, NewSize):  
        if self.AnimIgnoreNextResize:
            self.AnimIgnoreNextResize = False
            return
        
        self.StopAllAnim = True
        self.StopAllAnimTimer = time.time()
        
        Anims = [self.DishPosAnim, self.ScrollAnim]
        for Anim in Anims:
            if Anim.state() == 0:
                continue
            Anim.stop()
            Anim.targetObject().move(Anim.endValue())
            Anim.finished.emit()
        
    
    def ResizeScroll(self, NewSize):
        ContentSizeX = 681
        FreeSpaceRatio = 0.5
        
        FrameSizeX, FrameSizeY = self.ChooseMenu.width(), self.ChooseMenu.height()
        WindowSizeX, WindowSizeY = NewSize
        
        ScrollPosX = int((FrameSizeX - ContentSizeX)/2)
        ScrollPosY = int(FreeSpaceRatio * FrameSizeY) if self.EndMode == False else 0
        ScrollSizeX = self.ScrollArea.width()
        ScrollSizeY = int(FrameSizeY - ScrollPosY + 2)
        
        self.ScrollArea.setGeometry(ScrollPosX, ScrollPosY, ScrollSizeX, ScrollSizeY)

    def ResizeScrollItems(self, NewSize=None):
        ScrollPosX, ScrollPosY = self.ScrollArea.x(), self.ScrollArea.y()
        ScrollSizeX = self.ScrollArea.width()
        TransitionPosX, TransitionPosY = ScrollPosX + ScrollSizeX - 410, ScrollPosY + 1

        self.Transition1.move(TransitionPosX, TransitionPosY)
        self.Transition2.move(TransitionPosX, TransitionPosY)
            
        CurrentDishPosX, CurrentDishPosY = self.GetCurrentDishPos()
        self.CurrentDish.move(CurrentDishPosX, CurrentDishPosY - self.CurrentDish.height() + 150)
       
    def ResizeForButtons(self, NewSize=None):
        ScrollPosX = self.ScrollArea.x()
        ScrollPosY = self.ScrollArea.y() if self.EndMode == False else int(0.5 * self.ChooseMenu.height())
        ScrollSizeX = self.ScrollArea.width()
        
        self.AcceptButton.move(ScrollPosX + ScrollSizeX + 19, ScrollPosY - 147)
        self.RefuseButton.move(ScrollPosX + ScrollSizeX + 138, ScrollPosY - 147)
        self.CountFrame.move(ScrollPosX + ScrollSizeX + 24, ScrollPosY + 76)
        self.LeaveChooseButton.move(ScrollPosX + ScrollSizeX + 61, ScrollPosY + 195)
        
        if self.EndMode == False:
            self.UndoButton.move(ScrollPosX + ScrollSizeX + 24, ScrollPosY - 30)
            self.UndoText.move(self.UndoButton.x(), self.UndoButton.y())
            self.EndButton.move(ScrollPosX + ScrollSizeX + 24, ScrollPosY + 23)
            self.EndText.move(self.EndButton.x(), self.EndButton.y())
        else:
            self.BackChoiceButton.move(ScrollPosX + ScrollSizeX + 24, ScrollPosY - 30)
            self.BackChoiceText.move(self.BackChoiceButton.x(), self.BackChoiceButton.y())
            self.UpdateButton.move(ScrollPosX + ScrollSizeX + 24, ScrollPosY + 23)
            self.UpdateText.move(self.UpdateButton.x(), self.UpdateButton.y())
   
    def SpawnInScroll(self, CurrentDish):
        Dish = CurrentDish.findChild(QWidget, "Dish")
        Dish.setParent(None)
        CurrentDish.setParent(Dish)
        CurrentDish.hide()
        
        self.ScrollVBox.insertWidget(0, Dish)
        self.ScrollWidget.adjustSize()
        
     
    def RemoveLatestDishFromScroll(self):
        Dish = self.ScrollVBox.itemAt(0).widget()
        self.ReverseDish = Dish.findChild(QWidget, "Form")
        self.ReverseDish.setParent(self.ChooseMenu)
        Dish.setParent(None) 
        
        self.ScrollVBox.removeWidget(Dish)
        self.ScrollWidget = QWidget()
        self.ScrollWidget.setLayout(self.ScrollVBox)
        self.ScrollArea.takeWidget()
        self.ScrollArea.setWidget(self.ScrollWidget)
        
        self.ReverseDish.resize(Dish.size())
        self.ReverseDish.move(Dish.x(), Dish.y())
        Dish.setParent(self.ReverseDish) 
        Dish.move(0,0)
        self.ReverseDish.show()
    
    def GetDishInfo(self, Dish):
        Name = Dish.findChild(QWidget, "Name")
        Type_Season = Dish.findChild(QWidget, "Type_Season")
        Description = Dish.findChild(QWidget, "Description")
        IsDescShown = Dish.findChild(QWidget, "SeeMore").property("IsShown")
        
        return [Name.text(), Type_Season.property("Type"), [int(x) for x in Type_Season.property("Season")], Description.property("CompleteDesc"), IsDescShown]
     
    def AddCurrentDishToScroll(self, Event=None):
        if self.CurrentlyAnimating == True or not self.AcceptButton.isEnabled():
            return
        self.CurrentlyAnimating = True

        self.ScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.VerticalScrollBar.setEnabled(False)
        self.VerticalScrollBar.setValue(0)

        def AnimEnded(): 
            self.ActionHistory.append((True, None))
            
            self.ScrollArea.move(self.ScrollArea.x(), self.ScrollArea.y() - self.CurrentDish.height() - 10)
            self.IncrementCount(self.CurrentDish, 1)
            self.SpawnInScroll(self.CurrentDish)
            self.VerticalScrollBar.setEnabled(True)
            self.ScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            self.UndoButton.setEnabled(True)
            self.UndoText.setEnabled(True)
            self.EndButton.setEnabled(True)
            self.EndText.setEnabled(True)
            self.CurrentDish.lower()
            self.SummonDish()  
            
        self.ScrollAnim = QPropertyAnimation(self.ScrollArea, b"pos")
        self.ScrollAnim.setEndValue(QPoint(self.ScrollArea.x(), self.ScrollArea.y() + self.CurrentDish.height() + 10))
        self.ScrollAnim.setDuration(300)

        self.DishPosAnim = QPropertyAnimation(self.CurrentDish, b"pos")
        self.DishPosAnim.setEndValue(QPoint(self.CurrentDish.x(), self.CurrentDish.y() + self.CurrentDish.height() + 10))
        self.DishPosAnim.setDuration(300)
            
        self.StartAnim(self.DishPosAnim, lambda:None)
        self.StartAnim(self.ScrollAnim, AnimEnded)
  
    def AnimateReverseDishOutsideScroll(self):
        self.ScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.VerticalScrollBar.setEnabled(False)
        self.VerticalScrollBar.setValue(0)
        DishBeingAnimated = self.ScrollVBox.itemAt(0).widget()

        def AnimEnded():
            self.RemoveLatestDishFromScroll()
            self.CurrentDish = self.ReverseDish
            self.IncrementCount(self.CurrentDish, -1)
            
            self.ReloadWindow()

            if self.ScrollVBox.count() == 0:
                self.UndoButton.setEnabled(False)
                self.UndoText.setEnabled(False)
                self.EndButton.setEnabled(False)
                self.EndText.setEnabled(False)
            
            self.VerticalScrollBar.setEnabled(True)
            self.ScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            self.AnimCompleted()
            
        self.ScrollAnim = QPropertyAnimation(self.ScrollArea, b"pos")
        self.ScrollAnim.setEndValue(QPoint(self.ScrollArea.x(), self.ScrollArea.y() - DishBeingAnimated.height() - 10))
        self.ScrollAnim.setDuration(300)

        self.StartAnim(self.ScrollAnim, AnimEnded)
        self.ScrollArea.resize(self.ScrollArea.width(), self.ScrollArea.height() + DishBeingAnimated.height() + 10)
        
    def RefuseDish(self, Event=None):
        if self.CurrentlyAnimating == True or not self.RefuseButton.isEnabled():
            return
        self.CurrentlyAnimating = True
        
        def AnimEnded():
            self.CurrentDish.hide()
            self.UndoButton.setEnabled(True)
            self.UndoText.setEnabled(True)
            self.ActionHistory.append((False, self.GetDishInfo(self.CurrentDish)))
            self.SummonDish()

        self.DishPosAnim = QPropertyAnimation(self.CurrentDish, b"pos")
        self.DishPosAnim.setEndValue(QPoint(-400, self.CurrentDish.y()))
        self.DishPosAnim.setDuration(300)
        
        self.StartAnim(self.DishPosAnim, AnimEnded)
        
    def ReverseRefuseDish(self):
        CurrentDishPosX, CurrentDishPosY = self.GetCurrentDishPos(self.ReverseDish)
        
        def AnimEnded():
            self.ReverseDish.show()
            self.CurrentDish = self.ReverseDish
            self.AnimCompleted()
            self.RemoveGlitches()
            
            if len(self.ActionHistory) == 0:
                self.UndoButton.setEnabled(False)
                self.UndoText.setEnabled(False)

        self.DishPosAnim = QPropertyAnimation(self.ReverseDish, b"pos")
        self.DishPosAnim.setEndValue(QPoint(CurrentDishPosX, CurrentDishPosY))
        self.DishPosAnim.setDuration(300)
        self.ReverseDish.move(-400, CurrentDishPosY)
        self.ReverseDish.show()
        
        self.StartAnim(self.DishPosAnim, AnimEnded)
       
    def ReverseChoice(self, Event=None):
        if self.CurrentlyAnimating == True or not self.UndoButton.isEnabled() :
            return
        self.CurrentlyAnimating = True
        
        WasAccepted, CurrentDishInfo = self.ActionHistory.pop()
        
        if WasAccepted:
            self.ReverseSummonDish(self.AnimateReverseDishOutsideScroll)
        else:
            self.ReverseDish = self.CreateDishUi(CurrentDishInfo[0], CurrentDishInfo[1], CurrentDishInfo[2], CurrentDishInfo[3], False, CurrentDishInfo[4])
            self.ReverseDish.hide()
            self.ReverseSummonDish(self.ReverseRefuseDish)
            
    def EndChoosingAnimation(self):
        self.ScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.Transition1.hide()
        self.Transition2.hide()
        
        def AnimEnded():
            self.ScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            self.ResizeForButtons()
            self.AcceptButton.setEnabled(False)
            self.RefuseButton.setEnabled(False)
            self.UndoButton.setVisible(False)
            self.UndoText.setVisible(False)
            self.EndButton.setVisible(False)
            self.EndText.setVisible(False)
            self.BackChoiceButton.setVisible(True)
            self.BackChoiceText.setVisible(True)
            self.UpdateButton.setVisible(IsUpdateAvailable())
            self.UpdateText.setVisible(self.UpdateButton.isVisible())
            self.AnimCompleted()
            self.RemoveGlitches()
            
        self.ScrollAnim = QPropertyAnimation(self.ScrollArea, b"pos")
        self.ScrollAnim.setEndValue(QPoint(self.ScrollArea.x(), 0))
        self.ScrollAnim.setDuration(700)
        self.ScrollArea.resize(self.ScrollArea.width(), self.ChooseMenu.height())
        
        self.StartAnim(self.ScrollAnim, AnimEnded)
    
    def EndChoosing(self, Event=None):
        if self.CurrentlyAnimating == True or not self.EndButton.isEnabled():
            return
        self.CurrentlyAnimating = True
        self.EndMode = True
        self.ReverseSummonDish(self.EndChoosingAnimation)
        
    def BackChoiceAnimation(self, Event=None):
        if self.CurrentlyAnimating == True:
            return
        
        self.ScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        def AnimEnded():
            self.ScrollArea.resize(self.ScrollArea.width(), FrameSizeY - ScrollPosY + 2)
            self.SummonDish(self.BackChoice)
            self.AdjustTransition(self.VerticalScrollBar.value())

        FrameSizeY = self.ChooseMenu.height()
        ScrollPosX = self.ScrollArea.x()
        ScrollPosY = FrameSizeY//2
        self.ScrollAnim = QPropertyAnimation(self.ScrollArea, b"pos")
        self.ScrollAnim.setEndValue(QPoint(ScrollPosX, ScrollPosY))
        self.ScrollAnim.setDuration(700)
        self.EndMode = False
        self.CurrentlyAnimating = True
        
        self.StartAnim(self.ScrollAnim, AnimEnded)
        
    def BackChoice(self):
        self.CurrentlyAnimating = True
        self.ScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.AcceptButton.setEnabled(True)
        self.RefuseButton.setEnabled(True)
        self.UndoButton.setVisible(True)
        self.UndoText.setVisible(True)
        self.EndButton.setVisible(True)
        self.EndText.setVisible(True)
        self.BackChoiceButton.setVisible(False)
        self.BackChoiceText.setVisible(False)
        self.UpdateButton.setVisible(False)
        self.UpdateText.setVisible(False)
        self.ReloadWindow()
        
    def StartAnim(self, Anim, AnimEnded):
        if not self.StopAllAnim:
            Anim.start()
            Anim.finished.connect(AnimEnded)
        elif time.time() - self.StopAllAnimTimer > 0.05:
            self.StoppAllAnim = False
            Anim.start()
            Anim.finished.connect(AnimEnded)
        else:
            Anim.targetObject().move(Anim.endValue())
            AnimEnded()
            
    def AnimCompleted(self):
            def ended(): self.CurrentlyAnimating = False
            QTimer.singleShot(50, ended)
            # À cause de StartAnim
            
    def IncrementCount(self, Dish, Increment):
        Type_Season = Dish.findChild(QWidget, "Type_Season")
        Type = Type_Season.property("Type")
        if Type == 0:
            self.StarterCount += Increment
        elif Type == 1:
            self.DishCount += Increment
        elif Type == 2:
            self.DessertCount += Increment
        else:
            Warn("Unvalid type found while incrementing dish counter")
        
        StarterText = f"<b>{self.StarterCount}</b> Entrée{Plurial(self.StarterCount)}"
        DishText = f"<b>{self.DishCount}</b> Plat{Plurial(self.DishCount)}"
        DessertText = f"<b>{self.DessertCount}</b> Dessert{Plurial(self.DessertCount)}"
            
        self.StarterCountWidget.setText(StarterText)
        self.DishCountWidget.setText(DishText)
        self.DessertCountWidget.setText(DessertText)
        
        
    def ConnectSeeMore(self, Form, DescOpen):
        def ShowAnimInScroll(NewSize):
            def AnimEnded():
                self.AnimCompleted()
                SeeMore.setProperty("IsShown", True)
                
            def AnimStepped(NewValue):
                Dish.setMinimumSize(NewValue)
                Description.resize(Description.width(), NewValue.height() - 71)
                self.ScrollWidget.adjustSize()
                self.ScrollArea.updateGeometry()
            
            self.DishSizeAnim = QPropertyAnimation(Dish, b"size")
            self.DishSizeAnim.setEndValue(NewSize)
            self.DishSizeAnim.setDuration(300)
            self.DishSizeAnim.start()
            self.DishSizeAnim.finished.connect(AnimEnded)
            self.DishSizeAnim.valueChanged.connect(AnimStepped)
            
        def ShowAnimOutsideScroll(NewSize):
            def AnimEnded():
                self.AnimCompleted()
                SeeMore.setProperty("IsShown", True)
                
            def SizeAnimStepped(NewValue):
                Dish.setMinimumSize(NewValue)
                Description.resize(Description.width(), NewValue.height() - 71)
            
            self.DishSizeAnim = QPropertyAnimation(Dish, b"size")
            self.DishSizeAnim.setEndValue(NewSize)
            self.DishSizeAnim.setDuration(300)
            
            self.DishPosAnim = QPropertyAnimation(Form, b"pos")
            self.DishPosAnim.setEndValue(QPoint(Form.x(), Form.y() - NewSize.height() + Dish.height()))
            self.DishPosAnim.setDuration(300)
            
            self.DishPosAnim.start()
            self.DishSizeAnim.start()
            self.DishPosAnim.finished.connect(AnimEnded)
            self.DishSizeAnim.valueChanged.connect(SizeAnimStepped)
            
        def ShowInstantOutsideScroll(NewSize):
            Dish.setMinimumSize(NewSize)
            Dish.setSize(NewSize)
            Description.setSize(NewSize.width(), NewSize.height() - 71)
            Form.setPosition(QPoint(Form.x(), Form.y() - NewSize.height() + Dish.height()))
            self.AnimCompleted()
            SeeMore.setProperty("IsShown", True)
            
        def ShowDesc(NoAnim=False):
            DescriptionRect = Description.contentsRect()
            DescriptionSize = DescriptionRect.size()
            
            FontMetrics = QFontMetrics(Description.font())
            Text = Description.property("CompleteDesc")
            TextSize = FontMetrics.boundingRect(DescriptionRect, Qt.TextWordWrap, Text + "\n\n")
            
            SizeToAdd = TextSize.height() - DescriptionSize.height()
            NewSize = QSize(Dish.width(), Dish.height() + SizeToAdd)
            Form.setGeometry(Form.x(), Form.y(), Dish.width(), Dish.height() + SizeToAdd)
            
            if Form == self.CurrentDish:
                ShowInstantOutsideScroll(NewSize) if NoAnim else ShowAnimOutsideScroll(NewSize)
            else:
                ShowAnimInScroll(NewSize)
            
            Description.setText(Text)
            SeeMore.setGeometry(SeeMore.x(), Form.height() - 25, SeeMore.width(), SeeMore.height())
            FontMetrics = QFontMetrics(SeeMore.font())
            SeeMoreTextRect = FontMetrics.tightBoundingRect("Voir moins")
            SeeMore.setText("Voir moins")
            SeeMore.resize(SeeMoreTextRect.width() + 3, SeeMore.height())
            Separation.setGeometry(Separation.x(), Form.height() - 30, Separation.width(), Separation.height())
            Separation.show()
        
        def HideAnimEnded():
            self.AnimCompleted()
            SeeMore.setProperty("IsShown", False)
            Separation.hide()     
                
            FontMetrics = QFontMetrics(SeeMore.font())
            SeeMoreTextRect = FontMetrics.tightBoundingRect("Voir plus")
            SeeMore.resize(SeeMoreTextRect.width() + 3, SeeMore.height())
            SeeMore.setText("Voir plus")
            SeeMore.move(290, 118)
                
            Description.setText(Description.property("CroppedDesc"))
            Form.setGeometry(Form.x(), Form.y(), 400, 150)  
            
        def HideDescInScroll():
            def AnimStepped(NewValue):
                Dish.setMinimumSize(NewValue)
                Description.resize(Description.width(), NewValue.height() - 71)
                self.ScrollWidget.adjustSize()
                self.ScrollArea.updateGeometry()
                
            self.DishSizeAnim = QPropertyAnimation(Dish, b"size")
            self.DishSizeAnim.setEndValue(QSize(400, 150))
            self.DishSizeAnim.setDuration(300)
            self.DishSizeAnim.start()
            self.DishSizeAnim.finished.connect(HideAnimEnded)
            self.DishSizeAnim.valueChanged.connect(AnimStepped)
            
        def HideDescOutsideScroll():
            def AnimEnded():
                Description.resize(Description.width(), Dish.height() - 71)
            
            self.DishSizeAnim = QPropertyAnimation(Dish, b"size")
            self.DishSizeAnim.setEndValue(QSize(400, 150))
            self.DishSizeAnim.setDuration(300)
                
            Dish.setMinimumSize(QSize(400, 150))
            CurrentDishPosX, CurrentDishPosY = self.GetCurrentDishPos()
            
            self.DishPosAnim = QPropertyAnimation(Form, b"pos")
            self.DishPosAnim.setEndValue(QPoint(CurrentDishPosX, CurrentDishPosY))
            self.DishPosAnim.setDuration(300)
            
            self.DishSizeAnim.start()
            self.DishPosAnim.start()
            self.DishPosAnim.finished.connect(HideAnimEnded)
            self.DishSizeAnim.finished.connect(AnimEnded)
            
        def HideDesc():
            if Dish == self.CurrentDish.findChild(QWidget, "Dish"):
                HideDescOutsideScroll()
            else:
                HideDescInScroll()
            
        def OnClick(Event):
            if self.CurrentlyAnimating == True:
                return
            self.CurrentlyAnimating = True
                    
            IsShown = SeeMore.property("IsShown")
            if IsShown:
                HideDesc()
            else:
                ShowDesc()              
        
        Dish = Form.findChild(QWidget, "Dish")
        SeeMore = Dish.findChild(QWidget, "SeeMore")
        Separation = Dish.findChild(QWidget, "Separation")
        Description = Dish.findChild(QWidget, "Description")
        SeeMore.mousePressEvent = OnClick
        
        if DescOpen:
            ShowDesc(True)
        
    def LeaveChoose(self, Event):
        if self.ShowQuitConfirm():
            return
        
        self.Transition1.hide()
        self.Transition2.hide()
        self.ReverseSummonDish(self.CurrentDish.deleteLater)
        
        if not self.EndMode:
           self.StartLoading([self.CurrentDish, self.ScrollArea, self.AcceptButton, self.RefuseButton, self.UndoButton, self.UndoText, self.EndButton, self.EndText, self.CountFrame, self.LeaveChooseButton], self.LoadMainMenu)
           return
       
        if not IsUpdateAvailable():
            self.StartLoading([self.ScrollArea, self.AcceptButton, self.RefuseButton, self.BackChoiceButton, self.BackChoiceText, self.CountFrame, self.LeaveChooseButton], self.LoadMainMenu)
            return
        
        self.StartLoading([self.ScrollArea, self.AcceptButton, self.RefuseButton, self.BackChoiceButton, self.BackChoiceText, self.UpdateButton, self.UpdateText, self.CountFrame, self.LeaveChooseButton], self.LoadMainMenu)
    
    def RemoveGlitches(self):
        return
        if CompatibilitySize:
            Move = random.randrange(-1,2,2)
            OldSize = QSize(self.width(), self.height())
            NewSize = QSize(self.width() + Move, self.height())
            self.resize(NewSize)
            self.resize(OldSize)
            
    def ChooseKeyPressEvent(self, Event):            
        Key = Event.key()

        if Key == Qt.Key_Down:
            if self.EndMode:
                return False
            
            self.AddCurrentDishToScroll()
            return True
        
        if Key == Qt.Key_Left:
            if self.EndMode:
                return False
            
            self.RefuseDish()
            return True
        
        if Key == Qt.Key_Up:
            if self.EndMode:
                return False
            
            self.ReverseChoice()
            return True
        
        if Key == Qt.Key_Right:
           if self.EndMode:
               self.BackChoiceAnimation()
           else:
               self.EndChoosing()
           
           return True
            
        return False
    
    def NotEnoughSeasonMessage(self):
        global KeyOverride
        KeyOverride = False
        MessageBox = QMessageBox()
        MessageBox.setWindowTitle("Attention")
        MessageBox.setText("""<p style='text-align: center;'><img src=':/Images/Warning.png' alt='' width='100' height='100'></p>
                               <p style='text-align: center;'>Tous les plats de saison ont déjà été proposés</p>
                               <p style='text-align: center;'>Les prochains plats ne seront pas de saison</p>""")
        OkButton = MessageBox.addButton('Ok', QMessageBox.YesRole)
        StyleSheet = MessageStyleSheet(MessageBox)

        OkButton.setStyleSheet(StyleSheet)

        MessageBox.exec()
        KeyOverride = True
        
    def NotEnoughDishMessage(self):
        global KeyOverride
        KeyOverride = False
        MessageBox = QMessageBox()
        MessageBox.setWindowTitle("Attention")
        MessageBox.setText("""<p style='text-align: center;'><img src=':/Images/Warning.png' alt='' width='100' height='100'></p>
                               <p style='text-align: center;'>Tous les plats ont déjà été proposés</p>
                               <p style='text-align: center;'>Les prochains plats ne seront pas nouveaux</p>""")
        OkButton = MessageBox.addButton('Ok', QMessageBox.YesRole)
        StyleSheet = MessageStyleSheet(MessageBox)

        OkButton.setStyleSheet(StyleSheet)

        MessageBox.exec()
        KeyOverride = True
        
    def NoDishLeftMessage(self):
        global KeyOverride
        KeyOverride = False
        MessageBox = QMessageBox()
        MessageBox.setWindowTitle("Attention")
        MessageBox.setText("""<p style='text-align: center;'><img src=':/Images/Warning.png' alt='' width='100' height='100'></p>
                               <p style='text-align: center;'>Action impossible : plus aucun plat disponible</p>""")
        OkButton = MessageBox.addButton('Ok', QMessageBox.YesRole)
        StyleSheet = MessageStyleSheet(MessageBox)

        OkButton.setStyleSheet(StyleSheet)

        MessageBox.exec()
        KeyOverride = True
            
    def ShowQuitConfirm(self):
       global KeyOverride
       KeyOverride = False
       MessageBox = QMessageBox()
       MessageBox.setWindowTitle("Attention")
       MessageBox.setText("""<p style='text-align: center;'><img src=':/Images/Warning.png' alt='' width='100' height='100'></p>
                              <p style='text-align: center;'>Êtes-vous sûr de vouloir quitter ?</p>
                              <p style='text-align: center;'>La liste des plats sera perdue.</p>""")
       QuitButton = MessageBox.addButton('Quitter', QMessageBox.YesRole)
       CancelButton = MessageBox.addButton('Annuler', QMessageBox.NoRole)
       StyleSheet = MessageStyleSheet(MessageBox)

       QuitButton.setStyleSheet(StyleSheet)
       CancelButton.setStyleSheet(StyleSheet)

       Result = MessageBox.exec()
       KeyOverride = True
       return Result == 1
   
    def ShowQuitUpdate(self):
       global KeyOverride
       KeyOverride = False
       FormatedUpdateDescription = "<br>" + UpdateDescription.replace("\n", "</br>\n<br>") + "</br>"
        
       MessageBox = QMessageBox()
       MessageBox.setWindowTitle("Attention")
       MessageBox.setText(f"""<p style='text-align: center;'><img src=':/Images/UpdateLogo.png' alt='' width='100' height='100'></p>
                              <p style='text-align: center;'>Une mise à jour est disponible !</p>
                              <p style='text-align: center;'>Voici ce qui va changer : </p>
                              <p>{FormatedUpdateDescription}</p>""")
                             
       CancelButton = MessageBox.addButton('Annuler', QMessageBox.RejectRole)
       QuitButton = MessageBox.addButton('Ne pas mettre à jour', QMessageBox.NoRole)
       UpdateButton = MessageBox.addButton('Mettre à jour', QMessageBox.ActionRole)
       StyleSheet = MessageStyleSheet(MessageBox)

       QuitButton.setStyleSheet(StyleSheet)
       UpdateButton.setStyleSheet(StyleSheet)
       CancelButton.setStyleSheet(StyleSheet)
       MessageBox.setDefaultButton(CancelButton)
       
       Answer = MessageBox.exec()
       KeyOverride = True
    
       if Answer == 2:
           self.InstallUpdate()
           Answer = 1
       
       return Answer == 0
   
    def ShowUpdateConfirm(self, Event=None):
        global KeyOverride
        KeyOverride = False
        FormatedUpdateDescription = "<br>" + UpdateDescription.replace("\n", "</br>\n<br>") + "</br>"
        
        MessageBox = QMessageBox()
        MessageBox.setWindowTitle("Attention")
        MessageBox.setText(f"""<p style='text-align: center;'><img src=':/Images/Warning.png' alt='' width='100' height='100'></p>
                               <p style='text-align: center;'>Êtes-vous sûr de vouloir quitter ?</p>
                               <p style='text-align: center;'>Voici ce que la mise à jour va\n changer :</p>
                               <p>{FormatedUpdateDescription}</p>""")
        YesButton = MessageBox.addButton('Mettre à jour', QMessageBox.YesRole)
        CancelButton = MessageBox.addButton('Annuler', QMessageBox.NoRole)
        StyleSheet = MessageStyleSheet(MessageBox)

        YesButton.setStyleSheet(StyleSheet)
        CancelButton.setStyleSheet(StyleSheet)

        Answer = MessageBox.exec()
        KeyOverride = True
        
        if Answer == 1:
            return
        
        self.InstallUpdate()
   
    def ChooseMenuCloseEvent(self, Event):
        WindowSizeX, WindowSizeY = self.width(), self.height()
        WindowPosX, WindowPosY = self.x(), self.y()
        self.Settings.setValue("WindowSize", (WindowSizeX, WindowSizeY))
        self.Settings.setValue("WindowPos", (WindowPosX, WindowPosY))
        
        if IsUpdateAvailable() == False:
           KeepWindow = self.ShowQuitConfirm()
        else:
            KeepWindow = self.ShowQuitUpdate()
            
        if KeepWindow:
            Event.ignore()
        else:
            Event.accept()

#%% CreateMenu      
    def LoadCreateDish(self):
        global ImpactedWidgetDisplay, CustomResizeFunctions, KeyOverride, KeyOverrideFunc
        ImpactedWidgetDisplay = []
        CustomResizeFunctions = []
        KeyOverrideFunc = self.KeyPressEvent
        KeyOverride = True
        
        if time.time() > Timestamp + 31536000 and False:
            self.AppTooOld()
        
        self.StackedWidget.setCurrentIndex(2)
        
        self.Title = self.findChild(QWidget, "Title")
        self.NameEntry = self.findChild(QWidget, "NameEntry")
        self.TypeFrame = self.findChild(QWidget, "TypeFrame")
        self.Starter = self.findChild(QWidget, "Starter")
        self.Dish = self.findChild(QWidget, "DishButton")
        self.Dessert = self.findChild(QWidget, "Dessert")
        self.SeasonFrame = self.findChild(QWidget, "SeasonFrame")
        self.Spring = self.findChild(QWidget, "Spring")
        self.Summer = self.findChild(QWidget, "Summer")
        self.Automn = self.findChild(QWidget, "Automn")
        self.Winter = self.findChild(QWidget, "Winter")
        self.DescEntry = self.findChild(QWidget, "DescEntry")
        self.Cancel = self.findChild(QWidget, "Cancel")
        self.Save = self.findChild(QWidget, "Save")
        self.Success = self.findChild(QWidget, "Success")
        
        self.ClearEverything()
        
        self.Success.setVisible(False)
        self.NameEntry.setText("_")
        self.NameEntry.setText("")
        self.DescEntry.setPlainText("_")
        self.DescEntry.setPlainText("")
        self.FocusList = [self.NameEntry, self.Starter, self.Dish, self.Dessert, self.Spring, self.Summer, self.Automn, self.Winter, self.DescEntry, self.Cancel, self.Save]
        self.FocusFunction = [None, self.TypeButton0Press, self.TypeButton1Press, self.TypeButton2Press, self.SeasonButton0Press, self.SeasonButton1Press, self.SeasonButton2Press, self.SeasonButton3Press, None, self.CancelCreation, self.SaveDish]
        self.ClickFocus = [self.NameEntry, self.DescEntry]
        self.DownFocus = [None, 2, 3, 8, 8, 8, 8, 8, None, 0, 0]
        self.UpFocus = [None, 0, 1, 2, 0, 0, 0, 0, None, 8, 8]
        self.RightFocus = [None, 4, 4, 4, 5, 6, 7, 2, None, 10, 9]
        self.LeftFocus = [None, 7, 7, 7, 2, 4, 5, 6, None, 10, 9]
        self.CreatedDish = {'Name': "", 'Type': None, 'Season': [], 'Desc': ""}
        self.LastConditionCheck = False
        self.ClosingCreateDish = False
        self.SuccessAnim = QPropertyAnimation()
        self.TitleAnim = QPropertyAnimation()
        self.Timer = QTimer()
        
        FontSizeWidgets = [(self.Title, 40), (self.Success, 40), (self.NameEntry, 27), (self.Starter, 13), (self.Dish, 13), (self.Dessert, 13), (self.Spring, 13), (self.Summer, 13), (self.Automn, 13), (self.Winter, 13), (self.DescEntry, 15), (self.Cancel, 19), (self.Save, 19)]
        self.SetFixedSize(FontSizeWidgets)
        CustomResizeFunctions.append(self.ResizeCreateDish)
        
        self.Starter.mousePressEvent = self.TypeButton0Press
        self.Dish.mousePressEvent = self.TypeButton1Press
        self.Dessert.mousePressEvent = self.TypeButton2Press
        self.Spring.mousePressEvent = self.SeasonButton0Press
        self.Summer.mousePressEvent = self.SeasonButton1Press
        self.Automn.mousePressEvent = self.SeasonButton2Press
        self.Winter.mousePressEvent = self.SeasonButton3Press
        self.NameEntry.textChanged.connect(self.NameChanged)
        self.Cancel.mousePressEvent = self.CancelCreation
        self.Save.mousePressEvent = self.SaveDish
        self.closeEvent = self.CreateMenuCloseEvent
        
        self.NameEntry.setAttribute(Qt.WA_MacShowFocusRect, 0)
        self.NameEntry.setFocus()
        
        self.CreateMenuNeverActivated = False
        self.EndLoading([self.Title, self.NameEntry, self.TypeFrame, self.SeasonFrame, self.DescEntry, self.Cancel, self.Save])
        self.ReloadWindow()
    
    def ChangeFocus(self, CurrentWidget, NewFocusId):
        NewWidget = self.FocusList[NewFocusId]
        
        if CurrentWidget in self.ClickFocus:
            CurrentWidget.setFocusPolicy(Qt.ClickFocus)
            self.EditStyleSheetFocus(CurrentWidget, type(CurrentWidget), True)
        else:
            CurrentWidget.setFocusPolicy(Qt.NoFocus)
            
        if NewWidget in self.ClickFocus:
            self.EditStyleSheetFocus(NewWidget, type(NewWidget), False)
        
        NewWidget.setFocusPolicy(Qt.TabFocus)
        NewWidget.setFocus()
        self.FocusId = NewFocusId
    
    def KeyPressEvent(self, Event):            
        Key = Event.key()
        FocusId = self.FocusList.index(self.focusWidget())
        CurrentWidget = self.FocusList[FocusId]
        Type = type(CurrentWidget)

        if Key == Qt.Key_Tab:
            NewFocusId = (FocusId + 1) % len(self.FocusList)
            NewFocusId = 0 if NewFocusId == 10 and not self.Save.isEnabled() else NewFocusId
            self.ChangeFocus(CurrentWidget, NewFocusId)
            return True
        
        if Type in [QPlainTextEdit, QLineEdit]:
            return False

        if Key == Qt.Key_Down:
            NewFocusId = self.DownFocus[FocusId]
            self.ChangeFocus(CurrentWidget, NewFocusId)
            return True
        
        if Key == Qt.Key_Up:
            NewFocusId = self.UpFocus[FocusId]
            self.ChangeFocus(CurrentWidget, NewFocusId)
            return True
            
        if Key == Qt.Key_Right:
            NewFocusId = self.RightFocus[FocusId] 
            self.ChangeFocus(CurrentWidget, NewFocusId)
            return True
        
        if Key == Qt.Key_Left:
            NewFocusId = self.LeftFocus[FocusId]
            self.ChangeFocus(CurrentWidget, NewFocusId)
            return True
        
        if Key == Qt.Key_Return or Key == Qt.Key_Space:
            Widget = self.focusWidget()
            WidgetFunc = self.FocusFunction[FocusId]
            if WidgetFunc and Widget.isEnabled():
                WidgetFunc()
                return True
            else:
                return False
        
        return False
            
    def EditStyleSheetFocus(self, Widget, WidgetType, Hide):        
        WidgetTypeStr = "QLineEdit" if WidgetType == QLineEdit else "QPlainTextEdit"
        BaseStyleSheet = \
            WidgetTypeStr + """{color: black;
                           background-color: rgb(255,255,255);
                           border-radius: 20;
                           padding-left:10;
                           padding-right:10} """
        StyleSheet = BaseStyleSheet if Hide else BaseStyleSheet \
            + WidgetTypeStr + """:focus {border: 2px solid rgb(104,203,255)}"""
        Widget.setStyleSheet(StyleSheet)
        
    def EditSelectedButton(self, Widget, Select):
        Color = "rgb(167, 138, 242)" if Select else "rgb(220, 220, 220)"
        StyleSheet = """QLabel {background-color: """ + Color + """;
                                color: black;
                                border-radius: 15}
                        QLabel:focus {border: 2px solid rgb(104,203,255)}"""
        Widget.setStyleSheet(StyleSheet)
        Widget.setProperty("Activated", Select)
        
    def CheckNewDishConditions(self):
        if self.NameEntry.text() == "" \
        or self.CreatedDish["Type"] == None \
        or len(self.CreatedDish["Season"]) == 0:
            self.Save.setEnabled(False)
            self.LastConditionCheck = False
        else:
            self.Save.setEnabled(True)
            self.LastConditionCheck = True
        
    def TypeButton0Press(self, Event=None):
        self.CreatedDish["Type"] = 0
        self.CheckNewDishConditions()
        self.Starter.setChecked(True)
        
    def TypeButton1Press(self, Event=None):
        self.CreatedDish["Type"] = 1
        self.CheckNewDishConditions()
        self.Dish.setChecked(True)
        
    def TypeButton2Press(self, Event=None):
        self.CreatedDish["Type"] = 2
        self.CheckNewDishConditions()
        self.Dessert.setChecked(True)
        
    def SeasonButton0Press(self, Event=None):
        Activated = self.Spring.property("Activated")
        if Activated == False:
            self.CreatedDish["Season"].append(0)
        else:
            self.CreatedDish["Season"].remove(0)
        self.EditSelectedButton(self.Spring, not Activated)
        self.CheckNewDishConditions()
        
    def SeasonButton1Press(self, Event=None):
        Activated = self.Summer.property("Activated")
        if Activated == False:
            self.CreatedDish["Season"].append(1)
        else:
            self.CreatedDish["Season"].remove(1)
        self.EditSelectedButton(self.Summer, not Activated)
        self.CheckNewDishConditions()
        
    def SeasonButton2Press(self, Event=None):
        Activated = self.Automn.property("Activated")
        if Activated == False:
            self.CreatedDish["Season"].append(2)
        else:
            self.CreatedDish["Season"].remove(2)
        self.EditSelectedButton(self.Automn, not Activated)
        self.CheckNewDishConditions()

    def SeasonButton3Press(self, Event=None):
        Activated = self.Winter.property("Activated")
        if Activated == False:
            self.CreatedDish["Season"].append(3)
        else:
            self.CreatedDish["Season"].remove(3)
        self.EditSelectedButton(self.Winter, not Activated)
        self.CheckNewDishConditions()
        
    def NameChanged(self, NewText):
        if (self.LastConditionCheck == True and len(NewText) == 0) \
        or (self.LastConditionCheck == False and len(NewText) != 0):
            self.CheckNewDishConditions()
            
    def IsNameUnique(self, Name, DishList):
        for Dish in DishList:
            if Dish["Name"] == Name:
                return False
        return True
    
    def AnimateSuccess(self):
        def AnimEnded():
            if self.SuccessAnim.endValue() == 0:
                self.Success.hide()
        
        def HideSuccess():
            if self.ClosingCreateDish:
                return
            self.SuccessAnim.setEndValue(0)
            self.SuccessAnim.finished.connect(AnimEnded)
            self.SuccessAnim.start()
            if not sip.isdeleted(self.TitleOpacity):
                self.Title.show()
                self.TitleAnim.start()
            
        self.Success.show()
        self.Title.hide()
        self.SuccessAnim.stop()
        self.TitleAnim.stop()
        self.Timer.stop()
        
        self.SuccessOpacity = QGraphicsOpacityEffect()
        self.SuccessOpacity.setOpacity(0)
        self.Success.setGraphicsEffect(self.SuccessOpacity)
        self.TitleOpacity = QGraphicsOpacityEffect()
        self.TitleOpacity.setOpacity(0)
        self.Title.setGraphicsEffect(self.TitleOpacity)
        
        self.SuccessAnim = QPropertyAnimation(self.SuccessOpacity, b"opacity")
        self.SuccessAnim.setEndValue(1)
        self.SuccessAnim.setDuration(500)
        
        self.TitleAnim = QPropertyAnimation(self.TitleOpacity, b"opacity")
        self.TitleAnim.setEndValue(1)
        self.TitleAnim.setDuration(500)
        
        self.SuccessAnim.start()
        
        self.Timer = QTimer()
        self.Timer.timeout.connect(HideSuccess)
        self.Timer.setSingleShot(True)
        self.Timer.start(3000)
    
    def InsertDishAlphabetically(self, DishList, DishName):
        MaxId = len(DishList) - 1
        DishName = DishName.casefold()
        i = 0
        for i, Dish in enumerate(DishList):
            if Dish["Name"].casefold() > DishName:
                break
            elif i == MaxId:
                i += 1

        return i
    
    def ClearEverything(self):
        self.NameEntry.setText("")
        for RadioButton in [self.Starter, self.Dish, self.Dessert]:
            if RadioButton.isChecked() == True:
                RadioButton.setAutoExclusive(False)
                RadioButton.setChecked(False)
                RadioButton.setAutoExclusive(True)
        for SeasonAndFunc in [(self.Spring, self.SeasonButton0Press), (self.Summer, self.SeasonButton1Press), (self.Automn, self.SeasonButton2Press), (self.Winter, self.SeasonButton3Press)]:
            if SeasonAndFunc[0].property("Activated") == True:
                SeasonAndFunc[1]()
        self.DescEntry.setPlainText("")
        self.CreatedDish = {'Name': "", 'Type': None, 'Season': [], 'Desc': ""}
    
    def SaveDish(self, Event=None):
        Name = self.NameEntry.text()
        Season = self.CreatedDish["Season"]
        Season.sort()
        Desc = self.DescEntry.toPlainText()
        DishList = self.Settings.value("DishList")
        
        if not self.IsNameUnique(Name, DishList):
            self.NameAlreadyExists()
            return
        
        self.CreatedDish["Name"] = Name
        self.CreatedDish["Season"] = Season
        self.CreatedDish["Desc"] = Desc
        
        Placement = self.InsertDishAlphabetically(DishList, Name)
        DishList.insert(Placement, self.CreatedDish)
        self.UpdateDishList(DishList)
        
        self.ClearEverything()
        
        self.AnimateSuccess()
        self.NameEntry.setFocus()
        
    def AreEntryEmpty(self):
        Name = self.NameEntry.text()
        Type = self.CreatedDish["Type"]
        Season = self.CreatedDish["Season"]
        Desc = self.DescEntry.toPlainText()
        
        if (Name != "" \
        or Type != None \
        or Season != [] \
        or Desc != ""):
            return False
        else:
            return True
    
    def CancelCreation(self, Event=None):        
        if not self.AreEntryEmpty() and self.ShowCreateQuitConfirm() == True:
            return
        
        self.Success.hide()
        self.Title.show()
        self.ClosingCreateDish = True
        self.StartLoading([self.Title, self.NameEntry, self.TypeFrame, self.SeasonFrame, self.DescEntry, self.Cancel, self.Save], self.LoadMainMenu)
        
    def NameAlreadyExists(self):
        global KeyOverride
        KeyOverride = False
        
        MessageBox = QMessageBox()
        MessageBox.setWindowTitle("Attention")
        MessageBox.setText("""<p style='text-align: center;'><img src=':/Images/Warning.png' alt='' width='100' height='100'></p>
                               <p style='text-align: center;'>Ce nom de plat existe déjà !</p>""")
        OkButton = MessageBox.addButton('Ok', QMessageBox.YesRole)
        StyleSheet = MessageStyleSheet(MessageBox)

        OkButton.setStyleSheet(StyleSheet)

        MessageBox.exec()
        KeyOverride = True
        
        
    def ShowCreateQuitConfirm(self):
       global KeyOverride
       KeyOverride = False
        
       MessageBox = QMessageBox()
       MessageBox.setWindowTitle("Attention")
       MessageBox.setText("""<p style='text-align: center;'><img src=':/Images/Warning.png' alt='' width='100' height='100'></p>
                              <p style='text-align: center;'>Êtes-vous sûr de vouloir quitter ?</p>
                              <p style='text-align: center;'>Le plat sera perdu.</p>""")
       QuitButton = MessageBox.addButton('Quitter', QMessageBox.YesRole)
       CancelButton = MessageBox.addButton('Annuler', QMessageBox.NoRole)
       StyleSheet = MessageStyleSheet(MessageBox)

       QuitButton.setStyleSheet(StyleSheet)
       CancelButton.setStyleSheet(StyleSheet)
       
       Result = MessageBox.exec() == 1
       KeyOverride = True
       return Result
   
    def AppTooOld(self):
       global KeyOverride
       KeyOverride = False
        
       MessageBox = QMessageBox()
       MessageBox.setWindowTitle("Attention")
       MessageBox.setText("""<p style='text-align: center;'><img src=':/Images/Warning.png' alt='' width='100' height='100'></p>
                              <p style='text-align: center;'>Votre application ne permet pas de créer de nouveaux plats pour le moment et doit être mise à jour</p>""")
       OkButton = MessageBox.addButton('Ok', QMessageBox.YesRole)
       StyleSheet = MessageStyleSheet(MessageBox)

       OkButton.setStyleSheet(StyleSheet)
       
       MessageBox.exec()
       KeyOverride = True
       self.close()
    
    def ResizeCreateDish(self, WindowSize):
        FrameSizeX, FrameSizeY = WindowSize
        SizeX = 712
        SizeY = 523
        PosX = (FrameSizeX - SizeX)//2
        PosY = int(max(20, 0.25 * (FrameSizeY - SizeY)))
        
        TitlePosX = PosX
        TitlePosY = PosY
        self.Title.move(TitlePosX, TitlePosY)
        self.Success.move(TitlePosX, TitlePosY)
        
        NameEntryPosX = PosX
        NameEntryPosY = PosY + 102
        self.NameEntry.move(NameEntryPosX, NameEntryPosY)
        
        TypeFramePosX = int(PosX + 0.086 * SizeX)
        TypeFramePosY = PosY + 175
        self.TypeFrame.move(TypeFramePosX, TypeFramePosY)
        
        SeasonFramePosX = int(PosX + 0.310 * SizeX)
        SeasonFramePosY = PosY + 195
        self.SeasonFrame.move(SeasonFramePosX, SeasonFramePosY)
        
        DescEntryPosX = PosX
        DescEntryPosY = PosY + 309
        self.DescEntry.move(DescEntryPosX, DescEntryPosY)
        
        CancelPosX = SeasonFramePosX
        CancelPosY = PosY + 482
        self.Cancel.move(CancelPosX, CancelPosY)
        
        SavePosX = int(PosX + 0.549 * SizeX)
        SavePosY = CancelPosY
        self.Save.move(SavePosX, SavePosY)
        
    def CreateMenuCloseEvent(self, Event):
        WindowSizeX, WindowSizeY = self.width(), self.height()
        WindowPosX, WindowPosY = self.x(), self.y()
        self.Settings.setValue("WindowSize", (WindowSizeX, WindowSizeY))
        self.Settings.setValue("WindowPos", (WindowPosX, WindowPosY))
        
        if IsUpdateAvailable():
            KeepWindow = self.ShowQuitUpdate()
        elif not self.AreEntryEmpty():
            KeepWindow = self.ShowCreateQuitConfirm()
        else:
            KeepWindow = False
            
        if KeepWindow:
            Event.ignore()
        else:
            Event.accept()

#%% ModifyMenu              
    def LoadModifyMenu(self):
        global ImpactedWidgetDisplay, CustomResizeFunctions, KeyOverride, KeyOverrideFunc
        ImpactedWidgetDisplay = []
        CustomResizeFunctions = []
        KeyOverride = False
        KeyOverrideFunc = self.KeyPressEvent
        
        self.StackedWidget.setCurrentIndex(3)
        
        self.ScrollArea = self.findChild(QWidget, "ScrollArea2")
        self.Title = self.findChild(QWidget, "Title2")
        self.NameEntry = self.findChild(QWidget, "NameEntry2")
        self.TypeFrame = self.findChild(QWidget, "TypeFrame2")
        self.Starter = self.findChild(QWidget, "Starter2")
        self.Dish = self.findChild(QWidget, "DishButton2")
        self.Dessert = self.findChild(QWidget, "Dessert2")
        self.SeasonFrame = self.findChild(QWidget, "SeasonFrame2")
        self.Spring = self.findChild(QWidget, "Spring2")
        self.Summer = self.findChild(QWidget, "Summer2")
        self.Automn = self.findChild(QWidget, "Automn2")
        self.Winter = self.findChild(QWidget, "Winter2")
        self.DescEntry = self.findChild(QWidget, "DescEntry2")
        self.Cancel = self.findChild(QWidget, "Cancel2")
        self.Save = self.findChild(QWidget, "Save2")
        self.Success = self.findChild(QWidget, "Success2")
        self.Delete = self.findChild(QWidget, "Delete")
        
        self.ClearEverything()
        FontSizeWidgets = [(self.Title, 40), (self.Success, 40), (self.NameEntry, 27), (self.Starter, 13), (self.Dish, 13), (self.Dessert, 13), (self.Spring, 13), (self.Summer, 13), (self.Automn, 13), (self.Winter, 13), (self.DescEntry, 15), (self.Cancel, 19), (self.Save, 19), (self.Delete, 19)]
        self.SetFixedSize(FontSizeWidgets)

        self.Starter.mousePressEvent = self.TypeButton0Press       
        self.Dish.mousePressEvent = self.TypeButton1Press
        self.Dessert.mousePressEvent = self.TypeButton2Press
        self.Spring.mousePressEvent = self.SeasonButton0Press
        self.Summer.mousePressEvent = self.SeasonButton1Press
        self.Automn.mousePressEvent = self.SeasonButton2Press
        self.Winter.mousePressEvent = self.SeasonButton3Press
        self.Cancel.mousePressEvent = self.CancelModify
        self.Save.mousePressEvent = self.SaveModifiedDish
        self.Delete.mousePressEvent = self.DeleteModifiedDish
        self.NameEntry.textChanged.connect(self.NameChanged)
        self.NameEntry.setAttribute(Qt.WA_MacShowFocusRect, 0)
        self.Delete.setEnabled(False)
        
        self.Success.hide()
        self.TypeButtons = [self.Starter, self.Dish, self.Dessert]
        self.SeasonButtons = [self.Spring, self.Summer, self.Automn, self.Winter]
        self.EnableList = [self.NameEntry, self.Starter, self.Dish, self.Dessert, self.Spring, self.Summer, self.Automn, self.Winter, self.DescEntry]
        self.Window1List = [self.Title, self.NameEntry, self.TypeFrame, self.Starter, self.Dish, self.Dessert, self.SeasonFrame, self.Spring, self.Summer, self.Automn, self.Winter, self.DescEntry, self.Save, self.Delete]
        self.FocusList = [self.NameEntry, self.Starter, self.Dish, self.Dessert, self.Spring, self.Summer, self.Automn, self.Winter, self.DescEntry, self.Cancel, self.Save, self.Delete]
        self.FocusFunction = [None, self.TypeButton0Press, self.TypeButton1Press, self.TypeButton2Press, self.SeasonButton0Press, self.SeasonButton1Press, self.SeasonButton2Press, self.SeasonButton3Press, None, self.CancelCreation, self.SaveDish]
        self.ClickFocus = [self.NameEntry, self.DescEntry]
        self.DownFocus = [None, 2, 3, 8, 8, 8, 8, 8, None, 0, 0, 0]
        self.UpFocus = [None, 0, 1, 2, 0, 0, 0, 0, None, 8, 8, 8]
        self.RightFocus = [None, 4, 4, 4, 5, 6, 7, 2, None, 10, 11, 9]
        self.LeftFocus = [None, 7, 7, 7, 2, 4, 5, 6, None, 11, 9, 10]
        
        for Widget in self.EnableList:
            Widget.setDisabled(True)
        
        self.VerticalScrollBar = self.ScrollArea.verticalScrollBar()
        self.CurrentlyAnimating = False
        self.LastConditionCheck = False
        self.ClosingCreateDish = False
        self.FullScreen = False if self.width() < 1175 else True
        self.DisplayedWindow = 0
        
        self.ScrollWidget = QWidget()
        self.CurrentDish = QWidget()
        self.ScrollVBox = QVBoxLayout(self.ScrollWidget)
        self.ScrollVBox.setAlignment(Qt.AlignTop)
        self.SuccessAnim = QPropertyAnimation()
        self.TitleAnim = QPropertyAnimation()
        self.Timer = QTimer()
        self.CreatedDish = {'Name': "", 'Type': -999, 'Season': [], 'Desc': ""}
        self.OldDish = {'Name': "", 'Type': -999, 'Season': [], 'Desc': ""}
        self.closeEvent = self.ModifyMenuCloseEvent
        CustomResizeFunctions.append(self.ResizeModifyDish)
        
        for Widget in self.Window1List:
            Widget.setVisible(self.FullScreen)
        
        self.ModifyMenuNeverActivated = False
        self.ReloadWindow()
        
        DishList = self.Settings.value("DishList")
        DishListMaxId = len(DishList) - 1
        
        def AddWidgetFromRange(Start, Stop):
            for i in range(Start, Stop + 1):
                DishData = DishList[i]
                Dish = self.CreateDishUi(DishData["Name"], DishData["Type"], DishData["Season"], DishData["Desc"], True)
                self.ScrollVBox.addWidget(Dish.findChild(QWidget, "Dish"))
        
        def FadeAnimEnded():
            AddWidgetFromRange(10, DishListMaxId)
            self.ScrollArea.takeWidget()
            self.ScrollArea.setWidget(self.ScrollWidget)
            self.VerticalScrollBar.setEnabled(True)
            self.ScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        if DishListMaxId < 10:
            AddWidgetFromRange(0, DishListMaxId)
            self.ScrollArea.setWidget(self.ScrollWidget)
            self.EndLoading([self.ScrollArea, self.Title, self.NameEntry, self.TypeFrame, self.SeasonFrame, self.DescEntry, self.Cancel, self.Save, self.Delete])
        else:
            AddWidgetFromRange(0, 9)
            self.ScrollArea.setWidget(self.ScrollWidget)
            EndedSignal = self.EndLoading([self.ScrollArea, self.Title, self.NameEntry, self.TypeFrame, self.SeasonFrame, self.DescEntry, self.Cancel, self.Save, self.Delete])
            EndedSignal.Connect(FadeAnimEnded)
            self.VerticalScrollBar.setEnabled(False)
            self.ScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            
    def ReplaceDishAlphabetically(self, DishList, OldDishName, NewDishName):
        if OldDishName == NewDishName:
            DishId = self.InsertDishAlphabetically(DishList, OldDishName) - 1
            return DishId, DishId
        
        
        OldDishId = self.InsertDishAlphabetically(DishList, OldDishName) - 1
        DishList.pop(OldDishId)
        
        NewDishId = self.InsertDishAlphabetically(DishList, NewDishName)
        DishList.insert(NewDishId, {"Name": "Une erreur s'est produite", "Type":1, "Season":[3], "Desc":""})
        return OldDishId, NewDishId
    
    def SaveModifiedDish(self, Event):
        Name = self.NameEntry.text()
        Type = self.CreatedDish["Type"]
        Season = self.CreatedDish["Season"]
        Season.sort()
        Desc = self.DescEntry.toPlainText()
        DishList = self.Settings.value("DishList")
        
        if Name != self.OldDish["Name"] and not self.IsNameUnique(Name, DishList):
            self.NameAlreadyExists()
            return
        
        self.CreatedDish["Name"] = Name
        self.CreatedDish["Season"] = Season
        self.CreatedDish["Desc"] = Desc
        
        OldPlacement, NewPlacement = self.ReplaceDishAlphabetically(DishList, self.OldDish["Name"], Name)
        DishList[NewPlacement] = self.CreatedDish
        self.UpdateDishList(DishList)
        self.OldDish = self.CreatedDish.copy()
        
        NewWidget = self.CreateDishUi(Name, Type, Season, Desc, True)
        self.ScrollVBox.itemAt(OldPlacement).widget().deleteLater()
        
        if NewPlacement > OldPlacement:
            self.ScrollVBox.insertWidget(NewPlacement+1, NewWidget.findChild(QWidget, "Dish"))
        else:
            self.ScrollVBox.insertWidget(NewPlacement, NewWidget.findChild(QWidget, "Dish"))
            
        self.Success.setText("Plat modifié avec succès !")
        self.AnimateSuccess()
        
        if not self.FullScreen:
            self.StartLoading([self.Title, self.NameEntry, self.TypeFrame, self.SeasonFrame, self.DescEntry, self.Cancel, self.Save, self.Delete], self.LoadModifyWindow0)
            
    def DeleteModifiedDish(self, Event):
        Name = self.NameEntry.text()
        DishList = self.Settings.value("DishList")
        
        if not self.ShowDeleteConfirm(Name):
            return
        
        Placement = self.InsertDishAlphabetically(DishList, Name) - 1
        DishList.pop(Placement)
        self.UpdateDishList(DishList)
        self.OldDish = {'Name': "", 'Type': None, 'Season': [], 'Desc': ""}
        
        self.ScrollVBox.itemAt(Placement).widget().deleteLater()
        self.ScrollVBox.update()
        self.ScrollWidget.adjustSize()
        
        self.Success.setText("Plat supprimé avec succès !")
        self.AnimateSuccess()
        self.ClearEverything()
        
        self.NameEntry.setEnabled(False)
        for Button in self.TypeButtons:
            Button.setEnabled(False)
        for Button in self.SeasonButtons:
            Button.setEnabled(False)
        self.DescEntry.setEnabled(False)
        self.CheckModifyDishConditions()
        
        if not self.FullScreen:
            self.StartLoading([self.Title, self.NameEntry, self.TypeFrame, self.SeasonFrame, self.DescEntry, self.Cancel, self.Save, self.Delete], self.LoadModifyWindow0)
        
    def LoadModifyWindow0(self):
        self.DisplayedWindow = 0
        for Widget in self.Window1List:
            Widget.hide()
        self.ScrollArea.show()
        self.Cancel.show()
        self.Cancel.setText("Quitter")
        
        global KeyOverride
        KeyOverride = False
        self.NameEntry.setFocus()
        
        self.ReloadWindow()
        self.EndLoading([self.ScrollArea, self.Cancel])
        
    def LoadModifyWindow1(self):
        self.DisplayedWindow = 1
        for Widget in self.FocusList:
            Widget.show()
        self.Title.show()
        self.TypeFrame.show()
        self.SeasonFrame.show()
        self.ScrollArea.hide()
        self.Cancel.setText("Retour")
        
        global KeyOverride
        KeyOverride = True
        self.NameEntry.setFocus()
        
        self.ReloadWindow()
        self.EndLoading([self.Title, self.NameEntry, self.TypeFrame, self.SeasonFrame, self.DescEntry, self.Cancel, self.Save, self.Delete])

    def CheckModifyDishConditions(self):
        if self.NameEntry.text() == "" \
        or self.CreatedDish["Type"] == None \
        or len(self.CreatedDish["Season"]) == 0:
            self.Save.setEnabled(False)
            self.Delete.setEnabled(False)
            self.LastConditionCheck = False
        else:
            self.Save.setEnabled(True)
            self.Delete.setEnabled(True)
            self.LastConditionCheck = True    

    def ConnectModifyDish(self, Dish):
        Name = Dish.findChild(QWidget, "Name")
        Type_Season = Dish.findChild(QWidget, "Type_Season")
        Desc = Dish.findChild(QWidget, "Description")
        ModifyDishButton = Dish.findChild(QWidget, "ModifyDishButton")
        
        def ModifyClicked(Event):
            self.NameEntry.setEnabled(True)
            for Button in self.TypeButtons:
                Button.setEnabled(True)
            for Button in self.SeasonButtons:
                Button.setEnabled(True)
            self.DescEntry.setEnabled(True)

            self.NameEntry.setText(Name.text())
            self.TypeButtons[Type_Season.property("Type")].setChecked(True)
            EnableSeasons = [int(x) for x in Type_Season.property("Season")]
            for i, Button in enumerate(self.SeasonButtons):
                if i in EnableSeasons:
                    self.EditSelectedButton(Button, True)
                else:
                    self.EditSelectedButton(Button, False)
            RawDesc = Desc.property("CompleteDesc") 
            self.DescEntry.setPlainText("" if RawDesc == "Aucune description" else RawDesc)
            
            self.OldDish = {'Name': Name.text(), 'Type': Type_Season.property("Type"), 'Season': EnableSeasons.copy(), 'Desc': Desc.property("CompleteDesc")}
            self.CreatedDish = {'Name': Name.text(), 'Type': Type_Season.property("Type"), 'Season': EnableSeasons, 'Desc': Desc.property("CompleteDesc")}
            self.CheckModifyDishConditions()
            
            self.DisplayedWindow = 1
            if self.FullScreen:
                global KeyOverride
                KeyOverride = True
                self.NameEntry.setFocus()
            else:
                self.StartLoading([self.ScrollArea, self.Cancel], self.LoadModifyWindow1)
            
            
        ModifyDishButton.mousePressEvent = ModifyClicked
        
    def HasDishBeenModified(self):
        if self.OldDish["Name"] != self.NameEntry.text() \
        or self.OldDish["Type"] != self.CreatedDish["Type"] \
        or self.OldDish["Season"] != self.CreatedDish["Season"] \
        or self.OldDish["Desc"] != self.DescEntry.toPlainText():
            return True
        else:
            return False
        
    def CancelModify(self, Event):
        if self.DisplayedWindow == 1 and self.FullScreen == False:
            self.StartLoading([self.Title, self.NameEntry, self.TypeFrame, self.SeasonFrame, self.DescEntry, self.Cancel, self.Save, self.Delete], self.LoadModifyWindow0)
            return
        
        if self.HasDishBeenModified() and self.ShowCreateQuitConfirm() == True:
            return
        
        self.Success.hide()
        if self.FullScreen:
            self.Title.show()
        
        self.StartLoading([self.ScrollArea, self.Title, self.NameEntry, self.TypeFrame, self.SeasonFrame, self.DescEntry, self.Cancel, self.Save, self.Delete], self.LoadMainMenu)
        
    def ResizeFullScreenModify(self, WindowSize, FullScreenChanged):
        FrameSizeX, FrameSizeY = WindowSize
        SizeX = 1185
        PosX = (FrameSizeX - SizeX)//2
        PosY = int(max(20, 0.25 * (FrameSizeY - 523)))
        
        ScrollPosX = PosX
        ScrollPosY = 0
        ScrollSizeX = 426
        ScrollSizeY = FrameSizeY
        self.ScrollArea.setGeometry(ScrollPosX, ScrollPosY, ScrollSizeX, ScrollSizeY)
        
        TitlePosX = int(PosX + 0.390 * SizeX)
        TitlePosY = PosY
        self.Title.move(TitlePosX, TitlePosY)
        self.Success.move(TitlePosX, TitlePosY)
        
        NameEntryPosX = TitlePosX
        NameEntryPosY = PosY + 102
        self.NameEntry.move(NameEntryPosX, NameEntryPosY)
        
        TypeFramePosX = int(PosX + 0.443 * SizeX)
        TypeFramePosY = PosY + 175
        self.TypeFrame.move(TypeFramePosX, TypeFramePosY)
        
        SeasonFramePosX = int(PosX + 0.580 * SizeX)
        SeasonFramePosY = PosY + 195
        self.SeasonFrame.move(SeasonFramePosX, SeasonFramePosY)
        
        DescEntryPosX = TitlePosX
        DescEntryPosY = PosY + 309
        self.DescEntry.move(DescEntryPosX, DescEntryPosY)
        
        CancelPosX = int(PosX + 0.488 * SizeX)
        CancelPosY = PosY + 482
        self.Cancel.move(CancelPosX, CancelPosY)
        
        SavePosX = CancelPosX + 171
        SavePosY = CancelPosY
        self.Save.move(SavePosX, SavePosY) 
        
        DeletePosX = SavePosX + 171
        DeletePosY = SavePosY
        self.Delete.move(DeletePosX, DeletePosY) 
        
        if FullScreenChanged:
            self.Cancel.setText("Quitter")
            self.ScrollArea.show()
            for Widget in self.Window1List:
                Widget.show()
        
    def ResizeWindow0Modify(self, WindowSize, FullScreenChanged):
        FrameSizeX, FrameSizeY = WindowSize
        SizeX = 577
        SizeY = FrameSizeY
        PosX = (FrameSizeX - SizeX)//2
        
        ScrollPosX = PosX
        ScrollPosY = 0
        ScrollSizeX = 426
        ScrollSizeY = SizeY
        self.ScrollArea.setGeometry(ScrollPosX, ScrollPosY, ScrollSizeX, ScrollSizeY)
        
        CancelPosX = ScrollPosX + 436
        CancelPosY = (FrameSizeY - 41)//2
        self.Cancel.move(CancelPosX, CancelPosY)
        
        if FullScreenChanged:
            self.Cancel.setText("Quitter")
            for Widget in self.Window1List:
                Widget.hide()
        
    def ResizeWindow1Modify(self, WindowSize, FullScreenChanged):
        FrameSizeX, FrameSizeY = WindowSize
        SizeX = 712
        SizeY = 523
        PosX = (FrameSizeX - SizeX)//2
        PosY = int(max(20, 0.25 * (FrameSizeY - SizeY)))
        
        TitlePosX = PosX
        TitlePosY = PosY
        self.Title.move(TitlePosX, TitlePosY)
        self.Success.move(TitlePosX, TitlePosY)
        
        NameEntryPosX = PosX
        NameEntryPosY = PosY + 102
        self.NameEntry.move(NameEntryPosX, NameEntryPosY)
        
        TypeFramePosX = int(PosX + 0.086 * SizeX)
        TypeFramePosY = PosY + 175
        self.TypeFrame.move(TypeFramePosX, TypeFramePosY)
        
        SeasonFramePosX = int(PosX + 0.310 * SizeX)
        SeasonFramePosY = PosY + 195
        self.SeasonFrame.move(SeasonFramePosX, SeasonFramePosY)
        
        DescEntryPosX = PosX
        DescEntryPosY = PosY + 309
        self.DescEntry.move(DescEntryPosX, DescEntryPosY)
        
        CancelPosX = int(PosX + 0.160 * SizeX)
        CancelPosY = PosY + 482
        self.Cancel.move(CancelPosX, CancelPosY)
        
        SavePosX = CancelPosX + 171
        SavePosY = CancelPosY
        self.Save.move(SavePosX, SavePosY)
        
        DeletePosX = SavePosX + 171
        DeletePosY = CancelPosY
        self.Delete.move(DeletePosX, DeletePosY)
        
        
        if FullScreenChanged:
            self.Cancel.setText("Retour")
            self.ScrollArea.hide()
        
    def ResizeModifyDish(self, WindowSize):
        OldFullScreen = self.FullScreen and True or False
        self.FullScreen = False if self.width() < 1175 else True
        FullScreenChanged = OldFullScreen != self.FullScreen
        
        if self.FullScreen:
            self.ResizeFullScreenModify(WindowSize, FullScreenChanged)
            return
            
        if self.DisplayedWindow == 0:
            self.ResizeWindow0Modify(WindowSize, FullScreenChanged)
        else:
            self.ResizeWindow1Modify(WindowSize, FullScreenChanged)
            
    def ShowDeleteConfirm(self, DishName):
       global KeyOverride
       KeyOverride = False
        
       MessageBox = QMessageBox()
       MessageBox.setWindowTitle("Attention")
       MessageBox.setText(f"""<p style='text-align: center;'><img src=':/Images/Warning.png' alt='' width='100' height='100'></p>
                              <p style='text-align: center;'>Êtes-vous sûr de vouloir supprimer « {DishName} » ?</p>
                              <p style='text-align: center;'>Cette action est irréversible.</p>""")
       QuitButton = MessageBox.addButton('Supprimer', QMessageBox.YesRole)
       CancelButton = MessageBox.addButton('Annuler', QMessageBox.NoRole)
       StyleSheet = MessageStyleSheet(MessageBox)

       QuitButton.setStyleSheet(StyleSheet)
       CancelButton.setStyleSheet(StyleSheet)
       
       Result = MessageBox.exec() == 0
       KeyOverride = True
       return Result
            
    
    def ModifyMenuCloseEvent(self, Event):
        WindowSizeX, WindowSizeY = self.width(), self.height()
        WindowPosX, WindowPosY = self.x(), self.y()
        self.Settings.setValue("WindowSize", (WindowSizeX, WindowSizeY))
        self.Settings.setValue("WindowPos", (WindowPosX, WindowPosY))
        
        if IsUpdateAvailable():
            KeepWindow = self.ShowQuitUpdate()
        elif self.HasDishBeenModified():
            KeepWindow = self.ShowCreateQuitConfirm()
        else:
            KeepWindow = False
            
        if KeepWindow:
            Event.ignore()
        else:
            Event.accept()
 
#%% SettingsMenu
    def LoadSettingsMenu(self):
        global ImpactedWidgetDisplay, CustomResizeFunctions, KeyOverride, KeyOverrideFunc
        ImpactedWidgetDisplay = []
        CustomResizeFunctions = []
        KeyOverride = True
        KeyOverrideFunc = self.SettingsKeyPress
        
        self.StackedWidget.setCurrentIndex(4)
        
        self.Selection = self.SettingsMenu.findChild(QWidget, "Selection")
        self.Menu0Button = self.SettingsMenu.findChild(QWidget, "Menu0")
        self.Menu1Button = self.SettingsMenu.findChild(QWidget, "Menu1")
        self.Menu2Button = self.SettingsMenu.findChild(QWidget, "Menu2")
        self.Menu3Button = self.SettingsMenu.findChild(QWidget, "Menu3")
        self.Menu4Button = self.SettingsMenu.findChild(QWidget, "Menu4")
        self.SettingsFrame = self.SettingsMenu.findChild(QWidget, "SettingsFrame")
        self.Version = self.SettingsMenu.findChild(QWidget, "Version")
        self.Lines = self.SettingsMenu.findChild(QWidget, "Lines")
        self.PyQtRef = self.SettingsMenu.findChild(QWidget, "PyQtRef")
        self.LatestVersion = self.SettingsMenu.findChild(QWidget, "LatestVersion")
        self.UpToDate = self.SettingsMenu.findChild(QWidget, "UpToDate")
        self.UpdateButton = self.SettingsMenu.findChild(QWidget, "UpdateButton2")
        self.UpdateText = self.SettingsMenu.findChild(QWidget, "UpdateText2")
        self.UpdateDesc = self.SettingsMenu.findChild(QWidget, "UpdateDesc")
        self.NetworkError = self.SettingsMenu.findChild(QWidget, "NetworkError")
        self.FeedbackError = self.SettingsMenu.findChild(QWidget, "FeedbackError")
        self.FeedbackText = self.SettingsMenu.findChild(QWidget, "FeedbackText")
        self.FeedbackContent = self.SettingsMenu.findChild(QWidget, "FeedbackContent")
        self.FeedbackButton = self.SettingsMenu.findChild(QWidget, "FeedbackButton")
        self.SettingsSuccess = self.SettingsMenu.findChild(QWidget, "SettingsSuccess")
        self.BackupAvailable = self.SettingsMenu.findChild(QWidget, "BackupAvailable")
        self.CurrentBackup = self.SettingsMenu.findChild(QWidget, "CurrentBackup")
        self.CurrentDesc = self.SettingsMenu.findChild(QWidget, "CurrentDesc")
        self.CurrentText = self.SettingsMenu.findChild(QWidget, "CurrentText")
        self.BackupScroll = self.SettingsMenu.findChild(QWidget, "BackupScroll")
        self.ResortInfo = self.SettingsMenu.findChild(QWidget, "ResortInfo")
        self.ResortButton = self.SettingsMenu.findChild(QWidget, "ResortButton")
        self.ResortText = self.SettingsMenu.findChild(QWidget, "ResortText")
        self.LeaveSettingsButton = self.SettingsMenu.findChild(QWidget, "LeaveSettings")
        
        if self.SettingsMenuNeverActivated:
            self.FeedbackContentFocusInEvent = self.FeedbackContent.focusInEvent
            self.FeedbackContentFocusOutEvent = self.FeedbackContent.focusOutEvent
            
        FontSizeWidgets = [(self.SettingsSuccess, 40), (self.Menu0Button, 16), (self.Menu1Button, 16), (self.Menu2Button, 16), (self.Menu3Button, 16), (self.Menu4Button, 16), (self.LeaveSettingsButton, 19), (self.BackupAvailable, 16), (self.CurrentDesc, 13), (self.CurrentText, 20), (self.FeedbackButton, 19), (self.FeedbackContent, 16), (self.FeedbackError, 16), (self.FeedbackText, 16), (self.LatestVersion, 16), (self.Lines, 16), (self.NetworkError, 16), (self.PyQtRef, 16), (self.ResortInfo, 16), (self.UpToDate, 16), (self.UpdateDesc, 16), (self.Version, 16)]
        self.SetFixedSize(FontSizeWidgets)
        
        self.Menu0 = [self.Version, self.Lines, self.PyQtRef]
        self.Menu1 = [self.BackupAvailable, self.CurrentBackup, self.BackupScroll]
        self.Menu2 = [self.NetworkError, self.FeedbackError, self.FeedbackText, self.FeedbackContent, self.FeedbackButton, self.SettingsSuccess]
        self.Menu3 = [self.ResortInfo, self.ResortButton, self.ResortText]
        self.Menu4 = [self.LatestVersion, self.UpToDate, self.UpdateButton, self.UpdateText, self.UpdateDesc, self.NetworkError]
        self.Menu1To4 = self.Menu1 + self.Menu2 + self.Menu3 + self.Menu4
        
        self.ShowList = [self.ShowMenu0, self.ShowMenu1, self.ShowMenu2, self.ShowMenu3, self.ShowMenu4]
        self.MenuList = [self.Menu0, self.Menu1, self.Menu2, self.Menu3, self.Menu4]
        self.ButtonList = [self.Menu0Button, self.Menu1Button, self.Menu2Button, self.Menu3Button, self.Menu4Button]
        self.DownFocus = [1, 2, 3, 4, 0]
        self.UpFocus = [4, 0, 1, 2, 3]

        for Item in self.Menu1To4:
            Item.hide()
        for Item in self.Menu0:
            Item.show()
        
        self.Version.setText(f"Version : <b>{AppVersion}</b>")
        self.Lines.setText(f"Lignes de code : <b>{LineCount}</b>")
        self.LastConditionCheck = False
        self.FeedbackOnCooldown = False
        self.LastButtonId = 0
        self.SettingsSuccessAnim = QPropertyAnimation()
        self.Timer = QTimer()
        self.Menu0Button.setFocus()
        
        self.Menu0Button.mousePressEvent = self.ShowMenu0
        self.Menu1Button.mousePressEvent = self.ShowMenu1
        self.Menu2Button.mousePressEvent = self.ShowMenu2
        self.Menu3Button.mousePressEvent = self.ShowMenu3
        self.Menu4Button.mousePressEvent = self.ShowMenu4
        self.UpdateButton.mousePressEvent = self.InstallUpdate
        self.UpdateText.mousePressEvent = self.InstallUpdate
        self.FeedbackButton.mousePressEvent = self.SendFeedback
        self.ResortButton.mousePressEvent = self.ResortDishList
        self.ResortText.mousePressEvent = self.ResortDishList
        self.LeaveSettingsButton.mousePressEvent = self.LeaveSettings
        self.FeedbackContent.textChanged.connect(self.FeedbackContentChanged)
        self.FeedbackContent.focusInEvent = self.OnFeedbackFocusIn
        self.FeedbackContent.focusOutEvent = self.OnFeedbackFocusOut
        
        CustomResizeFunctions.append(self.ResizeSettings)
        
        self.SettingsMenuNeverActivated = False
        self.ReloadWindow()
        
        self.EndLoading([self.Selection, self.SettingsFrame, self.LeaveSettingsButton])
        
    def ShowMenu0(self, Event=None):
        self.CurrentButtonChanged(0)
        self.Version.show()
        self.Lines.show()
        self.PyQtRef.show()
    
    def ShowMenu1(self, Event=None):
        self.CurrentButtonChanged(1)
        self.BackupAvailable.show()
        DishList = self.Settings.value("DishList")
        DishBackup = self.Settings.value("DishBackup")
        CurrentDishCount, CurrentDescCount = self.GetDishAndDescOfList(DishList)
        self.CurrentDesc.setText(f"{CurrentDishCount} plat{Plurial(CurrentDishCount)} • {CurrentDescCount} description{Plurial(CurrentDescCount)}")
        self.CurrentBackup.show()
        self.BackupScroll.show()
        self.BackupScrollLayout = QVBoxLayout()
        self.BackupScrollWidget = QWidget()
        self.BackupWidgetList = []

        TimestampList = list(DishBackup.keys())
        TimestampList.sort(reverse=True)

        for Timestamp in TimestampList:
            BackupWidget = QWidget()
            BackupParent = BackupModule()
            BackupParent.setupUi(BackupWidget)
            Backup = BackupParent.Backup
            Name = Backup.findChild(QWidget, "BackupName")
            Desc = Backup.findChild(QWidget, "BackupDesc")
            Accept = Backup.findChild(QWidget, "BackupAccept")
            
            FontSizeWidgets = [(Name, 20), (Desc, 13), (Accept, 13)]
            self.SetFixedSize(FontSizeWidgets)

            Backup.setProperty("Timestamp", Timestamp)
            Date = datetime.fromtimestamp(Timestamp)
            Year, Month, Day, Hour, Minute = Date.year, TwoChar(Date.month), TwoChar(Date.day), Date.hour, TwoChar(Date.minute)
            Name.setText(f"Version du {Day}/{Month}/{Year} à {Hour}:{Minute}")
            DishCount, DescCount = self.GetDishAndDescOfList(DishBackup[Timestamp])
            Desc.setText(f"{DishCount} plat{Plurial(DishCount)} • {DescCount} description{Plurial(DescCount)}")
            
            self.ConnectBackupAccept(Backup)
            self.BackupWidgetList.append(BackupWidget)
            self.BackupScrollLayout.addWidget(Backup)
        
        self.BackupScrollWidget.setLayout(self.BackupScrollLayout)
        self.BackupScroll.setWidget(self.BackupScrollWidget)
    
    def ShowMenu2(self, Event=None):
        self.CurrentButtonChanged(2)
        if not RequestSuccessful:
            self.NetworkError.show()
            return
        
        if IsUpdateAvailable():
            self.FeedbackError.show()
            return
        
        self.OldFeedbackText = self.FeedbackContent.toPlainText()
        self.FeedbackText.show()
        self.FeedbackContent.show()
        self.FeedbackButton.show()
        self.FeedbackContent.setPlainText("_")
        self.FeedbackContent.setPlainText(self.OldFeedbackText)
        
    def ShowMenu3(self, Event=None):
        self.CurrentButtonChanged(3)
        self.ResortInfo.show()
        self.ResortButton.show()
        self.ResortText.show()
       
    def ShowMenu4(self, Event=None):
        self.CurrentButtonChanged(4)
        if not RequestSuccessful:
            self.NetworkError.show()
            return
        
        self.LatestVersion.setText(f"Dernière version disponible : <b>{LatestVersion}</b>")
        self.UpdateDesc.setText("Nouveautés :\n" + UpdateDescription)
        
        self.LatestVersion.show()
        if IsUpdateAvailable():
            self.UpdateButton.show()
            self.UpdateText.show()
            self.UpdateDesc.show()
        else:
            self.UpToDate.show()
            
    def GetDishAndDescOfList(self, DishList):
        DishCount = 0
        DescCount = 0
        for Dish in DishList:
            DishCount += 1
            if Dish["Desc"] != "": DescCount += 1
        return DishCount, DescCount
    
    def ConnectBackupAccept(self, Backup):
        Button = Backup.findChild(QWidget, "BackupAccept")
        
        def OnClicked(Event):
            if not self.AcceptBackupConfirm():
                return

            Timestamp = Backup.property("Timestamp")
            DishBackup = self.Settings.value("DishBackup")
            self.UpdateDishList(DishBackup[Timestamp])
            self.ShowMenu1()
            
        Button.mousePressEvent = OnClicked
        
    def ResortDishList(self, Event):
        DishList = self.Settings.value("DishList")
        DishList.sort(key=lambda x: x["Name"].upper())
        self.Settings.setValue("DishList", DishList)
        self.SettingsSuccess.setText("Plats retriés !")
        self.SettingsSuccess.setStyleSheet("""background-color: rgb(98, 184, 55);
                                           border: 2px solid rgb(88, 166, 52);
                                           border-radius: 10px""")
        self.AnimateSettingsSuccess()
    
        
    def CurrentButtonChanged(self, CurrentButtonId):
        for Widget in self.MenuList[self.LastButtonId]:
            Widget.hide()
        
        NewButton = self.ButtonList[CurrentButtonId]
        NewButton.setFocusPolicy(Qt.TabFocus)
        NewButton.setFocus()
        self.LastButtonId = CurrentButtonId
            
    def UpdateFeedbackButton(self):
        if self.FeedbackContent.toPlainText() == "" or self.FeedbackOnCooldown:
            self.FeedbackButton.setEnabled(False)
            self.LastConditionCheck = False
        else:
            self.FeedbackButton.setEnabled(True)
            self.LastConditionCheck = True
            
    def FeedbackContentChanged(self):
        NewContent = self.FeedbackContent.toPlainText()
        if (NewContent == "" and self.LastConditionCheck) \
        or (NewContent != "" and not self.LastConditionCheck):
            self.UpdateFeedbackButton()
   
    def AnimateSettingsSuccess(self):
        def AnimEnded():
            if self.SettingsSuccessAnim.endValue() == 0:
                self.SettingsSuccess.hide()
        
        def HideSettingsSuccess():
            self.SettingsSuccessAnim.setEndValue(0)
            self.SettingsSuccessAnim.finished.connect(AnimEnded)
            self.SettingsSuccessAnim.start()
            
        self.SettingsSuccess.show()
        self.SettingsSuccessAnim.stop()
        self.Timer.stop()
        self.SettingsSuccessOpacity = QGraphicsOpacityEffect()
        self.SettingsSuccessOpacity.setOpacity(0)
        self.SettingsSuccess.setGraphicsEffect(self.SettingsSuccessOpacity)
        
        self.SettingsSuccessAnim = QPropertyAnimation(self.SettingsSuccessOpacity, b"opacity")
        self.SettingsSuccessAnim.setEndValue(1)
        self.SettingsSuccessAnim.setDuration(500)
        
        self.SettingsSuccessAnim.start()
        
        self.Timer = QTimer()
        self.Timer.timeout.connect(HideSettingsSuccess)
        self.Timer.setSingleShot(True)
        self.Timer.start(3000)
   
    def ShowFeedbackSuccess(self, Reply):
        Error = Reply.error()
        if Error == QNetworkReply.NoError:
            self.FeedbackContent.setPlainText("")
            BackgroundColor, BorderColor = "rgb(98, 184, 55)", "rgb(88, 166, 52)"
            Text = "Commentaire envoyé !"
        else:
            BackgroundColor, BorderColor = "rgb(223, 34, 20)", "rgb(174, 33, 24)"
            Text = "Une erreur est survenue"
        
        self.SettingsSuccess.setStyleSheet("""background-color: """ + BackgroundColor + """;
                                           border: 2px solid """ + BorderColor + """;
                                           border-radius: 10px""")
        self.SettingsSuccess.setText(Text)
        self.AnimateSettingsSuccess()
        self.FeedbackOnCooldown = False
        self.UpdateFeedbackButton()
    
    def SendFeedback(self, Event):
        UserPath = os.path.expanduser("~").encode()
        UserId = hashlib.sha256(UserPath).hexdigest()
        FeedbackText = self.FeedbackContent.toPlainText()
        
        Data = {
                 "content": None,
                 "embeds": [
                   {
                     "title": "🌟 New User Feedback Received",
                     "color": 3447003,
                     "fields": [
                       {
                         "name": "Version",
                         "value": AppVersion + " - " + OSName(sys.platform)
                       },
                       {
                         "name": "User Identifier",
                         "value": UserId,
                       },
                       {
                         "name": "Feedback",
                         "value": FeedbackText
                       }
                     ]
                   }
                 ],
                 "attachments": []
               }     
        
        JsonData = json.dumps(Data)
        JsonData = JsonData.encode()     
        
        self.FeedbackOnCooldown = True
        self.UpdateFeedbackButton()
        
        self.Request = QNetworkRequest(QUrl(FeedbackURL))
        self.Request.setTransferTimeout(5000)
        self.Request.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")
        self.NetworkManager = QNetworkAccessManager()
        self.NetworkManager.finished.connect(self.ShowFeedbackSuccess)
        self.NetworkManager.post(self.Request, QByteArray(JsonData))
        
    def LeaveSettings(self, Event):        
        self.StartLoading([self.Selection, self.SettingsFrame, self.LeaveSettingsButton], self.LoadMainMenu)
       
    def ResizeSettings(self, WindowSize):
        FrameSizeX, FrameSizeY = WindowSize
        
        SizeX = 736
        SizeY = 555
        PosX = (FrameSizeX - SizeX)//2
        PosY = (FrameSizeY - SizeY)//2
        DemiSpaceX = min(PosX//4, 15)
        
        SelectionPosX = PosX - DemiSpaceX
        SelectionPosY = PosY
        self.Selection.move(SelectionPosX, SelectionPosY)
        
        SettingsFramePosX = int(PosX + 0.353 * SizeX) + DemiSpaceX
        SettingsFramePosY = PosY
        self.SettingsFrame.move(SettingsFramePosX, SettingsFramePosY)
        
        LeaveSettingsPosX = int(PosX + 0.073 * SizeX) - DemiSpaceX
        LeaveSettingsPosY = int(PosY + 0.270 * SizeY)
        self.LeaveSettingsButton.move(LeaveSettingsPosX, LeaveSettingsPosY)
        
        SettingsSuccessPosX = int(PosX + 0.016 * SizeX)
        SettingsSuccessPosY = 40
        self.SettingsSuccess.move(SettingsSuccessPosX, SettingsSuccessPosY)
    
    def ChangeSettingsFocus(self, CurrentButtonId):
        LastButton = self.ButtonList[self.LastButtonId]
        CurrentButton = self.ButtonList[CurrentButtonId]
        
        LastButton.setFocusPolicy(Qt.NoFocus)
        CurrentButton.setFocusPolicy(Qt.ClickFocus)
        CurrentButton.setFocus()
        
        self.ShowList[CurrentButtonId]()
    
    def SettingsKeyPress(self, Event):            
        Key = Event.key()
        
        if Key == Qt.Key_Tab and not self.FeedbackContent.hasFocus():
            CurrentButtonId = self.DownFocus[self.LastButtonId]
            self.ChangeSettingsFocus(CurrentButtonId)
            return True

        if Key == Qt.Key_Down:
            CurrentButtonId = self.DownFocus[self.LastButtonId]
            self.ChangeSettingsFocus(CurrentButtonId)
            return True
        
        if Key == Qt.Key_Up:
            CurrentButtonId = self.UpFocus[self.LastButtonId]
            self.ChangeSettingsFocus(CurrentButtonId)
            return True
        
        return False
    
    def OnFeedbackFocusIn(self, Event):        
        self.Menu2Button.setStyleSheet("""
        QLabel {background-color: rgb(0,86,217);
                color: white;
                padding-right: 5px;
                padding-left: 3px;
                border-radius:5}
        QLabel::focus {background-color: rgb(0,86,217);
                       color:white}
                                       """)
                                       
        self.FeedbackContentFocusInEvent(Event)                              
    
    def OnFeedbackFocusOut(self, Event):
        self.Menu2Button.setStyleSheet("""
        QLabel {background-color: none;
                color: black;
                padding-right: 5px;
                padding-left: 3px;
                border-radius:5}
        QLabel::focus {background-color: rgb(0,86,217);
                       color:white}
                                       """)
        
        self.FeedbackContentFocusOutEvent(Event)
        
        
    def InstallUpdate(self, Event=None):
        if not AutoUpdateSupport:
            self.ManualUpdate()
            return
        
        self.Settings.setValue("LastVersion", AppVersion)
        self.Settings.setValue("ExpectedVersion", LatestVersion)
        os.system(UpdateCommands[sys.platform])
        self.closeEvent = self.NoCloseEvent
        self.close()
        
    def ManualUpdate(self, Event=None):
        MessageBox = QMessageBox()
        MessageBox.setWindowTitle("Attention")
        MessageBox.setText("""<p style='text-align: center;'><img src=':/Images/Warning.png' alt='' width='100' height='100'></p>
                               <p style='text-align: center;'>Vous allez être redirigé vers la page d'installation</p>
                               <p style='text-align: center;'>Vous y trouverez les instructions à suivre</p>""")
        CopyButton = MessageBox.addButton('Copier le lien', QMessageBox.YesRole)
        OkButton = MessageBox.addButton('Ok', QMessageBox.AcceptRole)
        CancelButton = MessageBox.addButton('Annuler', QMessageBox.RejectRole)
        StyleSheet = MessageStyleSheet(MessageBox)

        OkButton.setStyleSheet(StyleSheet)
        CopyButton.setStyleSheet(StyleSheet)
        CancelButton.setStyleSheet(StyleSheet)

        Answer = MessageBox.exec()

        if Answer == 2:
            return
        
        if Answer == 0:
            pyperclip.copy(DownloadFolder)
            return
        
        webbrowser.open(DownloadFolder)
        self.closeEvent = self.NoCloseEvent
        self.close()
            
    def AcceptBackupConfirm(self):
       MessageBox = QMessageBox()
       MessageBox.setWindowTitle("Attention")
       MessageBox.setText("""<p style='text-align: center;'><img src=':/Images/Warning.png' alt='' width='100' height='100'></p>
                              <p style='text-align: center;'>Êtes-vous sûr de vouloir revenir à cette version ?</p>
                              <p style='text-align: center;'>La version actuelle sera conservée.</p>""")
       QuitButton = MessageBox.addButton('Continuer', QMessageBox.YesRole)
       CancelButton = MessageBox.addButton('Annuler', QMessageBox.NoRole)
       StyleSheet = MessageStyleSheet(MessageBox)

       QuitButton.setStyleSheet(StyleSheet)
       CancelButton.setStyleSheet(StyleSheet)

       return MessageBox.exec() == 0
        
            
#%% Main functions    
    def ResizeEvent(self, event):   
        WindowSize = event.size()
        WindowSize = (WindowSize.width(), WindowSize.height())
        
        for Widget in ImpactedWidgetDisplay:
            DisplayInfo = WidgetDisplayInfo[Widget.objectName()]
            CenterPositionRatio, SizeRatio, AncherPoint, AspectRatio, MaximumSizeY = DisplayInfo["CenterPositionRatio"], DisplayInfo["SizeRatio"], DisplayInfo["AnchorPoint"], DisplayInfo["AspectRatio"], DisplayInfo["MaximumSizeY"]
            
            MaximumSize = (SizeRatio[0]*WindowSize[0], SizeRatio[1]*WindowSize[1])
            ActualSizeY = int(min(MaximumSize[0]/AspectRatio, MaximumSize[1], MaximumSizeY))
            Size = (int(ActualSizeY * AspectRatio), ActualSizeY)

            Position = (int(CenterPositionRatio[0]*WindowSize[0] - Size[0]*AncherPoint[0]), int(CenterPositionRatio[1]*WindowSize[1] - Size[1]*AncherPoint[1]))

            Widget.setGeometry(Position[0], Position[1], Size[0], Size[1])
            
        for Function in CustomResizeFunctions:
            Function(WindowSize)
 
            
if DEBUG_MODE:
    Warn("Debug mode is enabled")
    
if FORCE_UPDATE:
    Warn("Force update is enabled")
    
if NO_UPDATE_ERROR:
    Warn("No update error is enabled")
    
if __name__ == '__main__':
    #Windows compatibility
    if CompatibilitySize:
        os.environ["QT_SCALE_FACTOR"] = str(round(ScreenScaleFactor, 2))
        sys.argv += ['--style', 'fusion']
  
    #Window setup
    app = QApplication(sys.argv)
    screen = app.primaryScreen()
    QFontDatabase.addApplicationFont(":/Fonts/Inter-Regular.ttf")
    QFontDatabase.addApplicationFont(":/Fonts/Inter-Bold.ttf")
    app.setStyleSheet(GetStyleSheet((45, 45, 45, 1)))
    NewOverrideFocus = OverrideFocus()
    app.installEventFilter(NewOverrideFocus)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec())
  
#%% EOF