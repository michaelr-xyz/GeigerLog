#! /usr/bin/env python
# -*- coding: UTF-8 -*-

"""
gsup_spectro.py - GeigerLog support file to use Gamma-Spectrum data

include in programs with:
    import gsup_spectro
"""

###############################################################################
#    This file is part of GeigerLog.
#
#    GeigerLog is free softwar you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    GeigerLog is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with GeigerLog.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################

# File Format Converter:
# Link auf das Manual für das Programm "SPEDAC Pro for DOS, Format Conversion of Spectral Data from Nuclear Experiments".
# https://inis.iaea.org/records/7bk01-1n237/files/32042415.pdf?download=1
# Von 1986(!). Also 40 Jahre alt, und läuft auf DOS 3.1 mit nur 512 kByte (k wie kilo)



__author__          = "ullix"
__copyright__       = "Copyright 2016 - 2025"
__credits__         = [""]
__license__         = "GPL3"


from gsup_utils   import *
import gsup_spectro_cnf


g.IsotopeData = {
    # Gamma-Ray Standards  -  https://www.ezag.com/wp-content/uploads/2023/08/catalogue_section_gamma_ray_standards.pdf
    "Compton Edge"      : [],
    "Single Escape"     : [],
    "Double Escape"     : [],
    "Back Scatter"      : [],

    "511"               : [511],                                               # 511 keV annihilation
    "1022"              : [1022],                                              # double 511 keV annihilation

    "Ag-108"            : [30.309, 79.131, 433.938, 614.31, 722.91],           # http://www.lnhb.fr/nuclides/Ag-108m_tables.pdf
    "Am-241"            : [17, 26.3, 59.5409],                                 # https://www.ld-didactic.de/software/524221en/index_Left.htm#CSHID=Appendix%2FRa226.htm|StartTopic=Content%2FAppendix%2FRa226.htm|SkinName=Primary
                                                                               # https://en.wikipedia.org/wiki/Americium-241
    "Ba-133"            : [81, 356],                                           # https://www.gammaspectacular.com/blue/ba133-spectrum
    "Bi-212"            : [727.330],                                           # https://www.physik.uzh.ch/groups/baudis/darkmatter/theses/xenon/Te_Bachlorarbeit_2009.pdf
    "Co-57"             : [122.061],                                           # https://www.physik.uzh.ch/groups/baudis/darkmatter/theses/xenon/Te_Bachlorarbeit_2009.pdf
    "Co-60"             : [1173.237, 1332.501],                                # https://www.physik.uzh.ch/groups/baudis/darkmatter/theses/xenon/Te_Bachlorarbeit_2009.pdf
    "Cs-137"            : [661.657],                                           # https://www.physik.uzh.ch/groups/baudis/darkmatter/theses/xenon/Te_Bachlorarbeit_2009.pdf
    "Eu-152"            : [121.782, 344.28, 1408.006, 964.079, 1112.074],      # und mehr ..  https://www.gammaspectacular.com/blue/gamma-spectra/eu152-spectrum
    "Ga-67"             : [91.263, 93.307, 184.577, 208.939, 300.233, 393.529],# und mehr...  http://www.lnhb.fr/nuclides/Ga-67_tables.pdf
    "I-129"             : [29.67, 33.7, 39.58],                                # https://www.ezag.com/wp-content/uploads/2023/08/I-129.pdf
    "I-131"             : [80.1854, 163.930, 284.305, 364.490, 636.990, \
                           722.909],                                           # plus many more http://www.lnhb.fr/nuclides/I-131_tables.pdf
    "K-40"              : [1460.81],
    "La-133"            : [],                                                  # kein Gamma!, "Lanthanum-133 is an excellent positron-emitting diagnostic lanthanide" from: https://pmc.ncbi.nlm.nih.gov/articles/PMC9611457/
                                                                               # Daughters: Ba-133 (100.0%) (Radioactive)
    "Lu-176"            : [88.34, 201.83, 306.78, 400.99],                     # https://www.gammaspectacular.com/blue/lu176-spectrum
    "Na-22"             : [511, 1274.537, 1785.537],                           # High peak is sum of the 2 other! https://www.internetchemie.info/isotop.php?Kern=Na-22; 511keV from Positron Annihilation
    "Ra-223"            : [269.13],                                            # from: https://www.sciencedirect.com/science/article/pii/S1738573317308057
    "Ra-226"            : [53, 80, 186, 242, 295, 352, 609],                   # https://www.ld-didactic.de/software/524221en/Content/Appendix/Ra226.htm
    "Rn-222"            : [47, 78, 242, 295, 351, 609, 1120, 1760, 2200],      # https://www.radiacode.com/de/isotope/rn-222
    "Sr-90"             : [],                                                  # no gamma, beta only:  https://ehs.missouri.edu/sites/ehs/files/pdf/isotopedata/sr-90.pdf
    "Th-231"            : [84.3, 89.950, 89.957, 99.35, 124.9, 133.9, \
                           135.6, 163.2, 174.0, 217.7],                        # from: https://www.sciencedirect.com/science/article/pii/S1738573317308057
    "Th-232"            : [65, 88, 238, 338, 583, 727, 911, 1588, 2614],       # from: https://www.radiacode.com/eur/isotope/th-232 NOT 2614=Tl-208 was also listed
    "Th-234"            : [92.37, 92.79],                                      # from: https://www.sciencedirect.com/science/article/pii/S1738573317308057
    "Tl-208"            : [583.191, 2614.533],                                 # Thallium 208, https://www.physik.uzh.ch/groups/baudis/darkmatter/theses/xenon/Te_Bachlorarbeit_2009.pdf
    "U-234"             : [120.9],                                             # from: https://www.sciencedirect.com/science/article/pii/S1738573317308057
    "U-235"             : [96.4, 140.7, 143.7, 150.9, 163.2, 182.4, 185.6, \
                           194.8, 201.9, 205.1, 215.0, 221.1, 228.6, 233.2,\
                           240.6, 246.6, 266.1],                               # from: https://www.sciencedirect.com/science/article/pii/S1738573317308057
    "Y-88"              : [1836.1],                                            # Halflife: 106.6 d; https://www.ezag.com/wp-content/uploads/2023/08/catalogue_section_gamma_ray_standards.pdf
                                                                               # https://www.ezag.com/wp-content/uploads/2023/08/Y-88.pdf
}

if g.debug: g.IsotopeData.update({"Fantasy"       : [3333.333]})               # Fake use for devel


#init
def initSpectroGraph(reset=False, overwrite=False):
    """Make the Spectro graph using matplotlib"""

    defname = gd(sys._getframe().f_code.co_name)

    # List all calib lines into proglog
    cdprint(defname, f"CalibLines: \n{g.spectroCalibLines}")

    # is a valid database already opened?
    if g.spectroData is None or len(g.spectroData) <= 1:
        fprint(header("Show Spectro Graph"))
        efprint("No Data")
        return

    # is a database graph already being displayed ?
    if not overwrite:
        if g.figSpectro is not None:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle("CAUTION")
            critical  = """You want to open a new spectro database, but one is already open. It will be closed when you continue.
                         \nTo continue with opening the new one click ok. Otherwise click Cancel."""
            msg.setText(critical)
            msg.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
            msg.setDefaultButton(QMessageBox.StandardButton.Cancel)
            msg.setEscapeButton

            retval = msg.exec()
            if retval != 1024:
                fprint("Cancelled")
                return
            g.spectroPlotPointer.done(0)
    else:
        g.spectroPlotPointer.done(0)

    irdprint(defname, f"reset: {reset}")
    if reset:
        resetSpectroParams()

    #
    # make GUI layout
    #

    EditBoxLong     = 115
    EditBoxMedium   = 120
    EditBoxChannels = 75
    EditBoxShort    = 40
    EditBoxShort    = 30

    # channel cumulation
    cumvalue = QLineEdit()
    cumvalue.setToolTip("The number of channels to sum up as single channel")
    cumvalue.setText(str(g.spectroCumul))
    cumvalue.setFixedWidth(EditBoxShort)
    cumvalue.returnPressed.connect(lambda:  dlg.done(7))
    # cumvalue.editingFinished.connect(lambda:  dlg.done(7))
    # cumvalue.textEdited     .connect(lambda:  dlg.done(7))
    # cumvalue.textChanged    .connect(lambda:  dlg.done(7))


    # Apply cumvalue
    ApplyCumButton = QPushButton("Apply")
    ApplyCumButton.setStyleSheet("QPushButton")
    ApplyCumButton.setFixedWidth(79)
    ApplyCumButton.setAutoDefault(False)
    ApplyCumButton.setToolTip("Apply the Channel to Cum value")
    ApplyCumButton.clicked.connect(lambda:  dlg.done(7))

    cumstuff = QHBoxLayout()
    cumstuff.addWidget(cumvalue, alignment=Qt.AlignmentFlag.AlignLeft)
    cumstuff.addWidget(ApplyCumButton, stretch = 0, alignment=Qt.AlignmentFlag.AlignLeft)
    cumstuff.addWidget(QLabel(""))

    cumChannels = QLineEdit()
    cumChannels.setReadOnly(True)
    cumChannels.setStyleSheet("background-color:#eee;")
    cumChannels.setToolTip("The number of channels after cumulation")
    cumChannels.setText(f"{int(g.spectroDataLen / g.spectroCumul):0,.0f}")
    cumChannels.setFixedWidth(EditBoxChannels)

    cumCounts = QLineEdit()
    cumCounts.setReadOnly(True)
    cumCounts.setStyleSheet("background-color:#eee;")
    cumCounts.setToolTip("The number of counts in all channels")
    cumCounts.setText(f"{np.sum(g.spectroData[:, 1]):0.0f}")
    cumCounts.setFixedWidth(EditBoxMedium)


    # Clip-limits Energy
    g.spectroLeftClipBox = QLineEdit()
    g.spectroLeftClipBox.setFixedWidth(EditBoxLong)
    g.spectroLeftClipBox.setToolTip("The displayed leftmost Spectrum energy value.\
                                     \nTo set using the mouse, simply press and hold key 'CRTL', \
                                     \nthen click left/right mouse button to set left/right energy edge.")
    g.spectroLeftClipBox.setText(f"{g.spectroLeftClipEnergy:0.2f}")

    g.spectroRightClipBox = QLineEdit()
    g.spectroRightClipBox.setToolTip("The displayed rightmost Spectrum energy value.\
                                      \nTo set using the mouse, simply press and hold key 'CTRL', \
                                      \nthen click left/right mouse button to set left/right energy edge.")
    g.spectroRightClipBox.setText(f"{g.spectroRightClipEnergy:0.2f}")
    g.spectroRightClipBox.setFixedWidth(EditBoxLong)

    g.channelNumbers = QLineEdit()
    g.channelNumbers.setReadOnly(True)
    g.channelNumbers.setToolTip("The Number of channels currently selected for display")
    g.channelNumbers.setText(f"{len(g.clipEnergy):0,.0f}")
    g.channelNumbers.setMaximumWidth(EditBoxChannels)
    g.channelNumbers.setStyleSheet("background-color:#eee;")

    g.countNumbers = QLineEdit()
    g.countNumbers.setReadOnly(True)
    g.countNumbers.setToolTip("The Number of counts in currently selected channels")
    g.countNumbers.setText(f"{np.sum(g.clipCounts):0,.8g}")
    g.countNumbers.setMaximumWidth(EditBoxChannels)
    g.countNumbers.setStyleSheet("background-color:#eee;")


    # Fit-Clip-Limits Energy
    g.spectroLeftFitBox = QLineEdit()
    g.spectroLeftFitBox.setToolTip("The leftmost Spectrum energy value used for the fit.\nTo set using the mouse, \
                                   \nsimply click left/right mouse button to set left/right energy edge.")
    g.spectroLeftFitBox.setText(f"{g.spectroLeftFitEnergy:0.2f}")
    g.spectroLeftFitBox.setFixedWidth(EditBoxLong)

    g.spectroRightFitBox = QLineEdit()
    g.spectroRightFitBox.setToolTip("The rightmost Spectrum energy value used for the fit.\nTo set using the mouse, \
                                    \nsimply click left/right mouse button to set left/right energy edge.")
    g.spectroRightFitBox.setText(f"{g.spectroRightFitEnergy:0.2f}")
    g.spectroRightFitBox.setFixedWidth(EditBoxLong)

    g.channelFitNumbers = QLineEdit()
    g.channelFitNumbers.setReadOnly(True)
    g.channelFitNumbers.setToolTip("The Number of channels currently selected for Fit")
    g.channelFitNumbers.setText(f"{len(g.clipFitEnergy)}")
    g.channelFitNumbers.setMaximumWidth(EditBoxChannels)
    g.channelFitNumbers.setStyleSheet("background-color:#eee;")

    g.countFitNumbers = QLineEdit()
    g.countFitNumbers.setReadOnly(True)
    g.countFitNumbers.setToolTip("The Number of counts in currently selected channels for Fit")
    g.countFitNumbers.setMaximumWidth(EditBoxChannels)
    g.countFitNumbers.setStyleSheet("background-color:#eee;")
    g.countFitNumbers.setText(f"")


    #
    # Checkboxes Plot Spectrum and other curves
    #

    # Check Plot Spectrum Fit
    def toggleSpectrumFit():
        g.spectroShowFit = g.checkFit.isChecked()
        if g.spectroShowFit: makeFitPeak()
        plotGraphSpectro()

    g.checkFit = QCheckBox("Fit")
    g.checkFit.setTristate(False)
    g.checkFit.setChecked(g.spectroShowFit)
    g.checkFit.setToolTip("Plot the fitted curve")
    g.checkFit.checkStateChanged.connect(lambda:  toggleSpectrumFit())


    # Check Show current Channel Width
    def toggleShowChnlW():
        g.spectroShowChnlW = checkShowChnlW.isChecked()
        plotGraphSpectro()

    checkShowChnlW = QCheckBox("W-Calib")
    checkShowChnlW.setChecked(g.spectroShowChnlW)
    checkShowChnlW.setToolTip("Show the original calibration Channel-Width curve")
    checkShowChnlW.stateChanged.connect(lambda:  toggleShowChnlW())


    # Check Show Orig calibration for Channel Width
    def toggleShowOrig():
        g.spectroShowOrig = checkShowOrig.isChecked()
        plotGraphSpectro()

    checkShowOrig = QCheckBox("W-Orig")
    checkShowOrig.setChecked(g.spectroShowOrig)
    checkShowOrig.setToolTip("Show the original calibration Channel-Width curve")
    checkShowOrig.stateChanged.connect(lambda:  toggleShowOrig())

    # Check Spectro Show Grid
    def toggleShowGrid():
        g.spectroShowGrid = checkShowGrid.isChecked()
        cdprint(defname, f"g.spectroShowGrid: {g.spectroShowGrid}")
        plotGraphSpectro()

    checkShowGrid = QCheckBox("Grid")
    checkShowGrid.setChecked(g.spectroShowGrid)
    checkShowGrid.setToolTip("Show the Grid in the Graph")
    checkShowGrid.stateChanged.connect(lambda:  toggleShowGrid())


    # Check Show Log
    def toggleShowLog():
        g.spectroShowLog = checkShowLog.isChecked()
        plotGraphSpectro()

    checkShowLog = QCheckBox("Log")
    checkShowLog.setChecked(g.spectroShowLog)
    checkShowLog.setToolTip("Show the Log of Spectrum in the Graph")
    checkShowLog.stateChanged.connect(lambda:  toggleShowLog())


    # Check Show Lines
    def toggleShowLine():
        g.spectroShowLine = checkShowLine.isChecked()
        plotGraphSpectro()

    checkShowLine = QCheckBox("Lines")
    checkShowLine.setChecked(g.spectroShowLine)
    checkShowLine.setToolTip("Show connecting lines between dots")
    checkShowLine.stateChanged.connect(lambda:  toggleShowLine())


    # reset Energies
    ResetClipButton = QPushButton("Reset Clip")
    ResetClipButton.setStyleSheet("QPushButton")
    ResetClipButton.setAutoDefault(False)
    ResetClipButton.setToolTip("Reset limits of Clip Energy to default")
    ResetClipButton.clicked.connect(lambda:  resetClip())


    # Fit Gauss curve
    FitButton = QPushButton("Fit Peak")
    FitButton.setStyleSheet("QPushButton")
    FitButton.setAutoDefault(False)
    FitButton.setToolTip("Fit a Gauss curve to the data within the FIT energies")
    FitButton.clicked.connect(lambda:  getPeakFitROI())


    # reset Fit
    ResetFitButton = QPushButton("Reset Fit")
    ResetFitButton.setStyleSheet("QPushButton")
    ResetFitButton.setAutoDefault(False)
    ResetFitButton.setToolTip("Reset limits of Fit Energy to default")
    ResetFitButton.clicked.connect(lambda:  resetFit())


    # select Gamma Lines
    GammaLinesButton = QPushButton("Isotopes")
    GammaLinesButton.setAutoDefault(False)
    GammaLinesButton.setToolTip("Select Isotopes for Fitting and Plotting")
    GammaLinesButton.clicked.connect(lambda:  selectIsotopes())

    # make calibration
    CalibPeakButton = QPushButton("Calibration")
    CalibPeakButton.setAutoDefault(False)
    CalibPeakButton.setToolTip("Calibration by Peaks and Formula")
    CalibPeakButton.clicked.connect(lambda:  Calibration())


    # apply Clip
    ClipEnergyButton = QPushButton("Clip")
    ClipEnergyButton.setAutoDefault(False)
    ClipEnergyButton.setToolTip("Clip the spectrum left and right")
    ClipEnergyButton.clicked.connect(lambda:  dlg.done(1))


    #layout GraphOptions
    graphOptions=QGridLayout()
    graphOptions.setContentsMargins(0, 0, 0, 0) # spacing around the graph options top=9 is adjusted for fit!
    # graphOptions.setColumnStretch (1, 200)
    # graphOptions.setColumnStretch (5, 1)
    # graphOptions.setColumnStretch (6, 1)
    # graphOptions.setRowStretch (0, 1)
    # graphOptions.setRowStretch (1, 1)
    # graphOptions.setColumnMinimumWidth(0, 60) # max gibt es nich

    # right side; graph
    labelWidth = 70
    r0Label = QLabel("Graph:")
    r0Label.setFont(g.fatfont)
    r0Label.setMaximumWidth(labelWidth)
    r1Label = QLabel("Clip:")
    r1Label.setMaximumWidth(labelWidth)
    r2Label = QLabel("Fit:")
    r2Label.setMaximumWidth(labelWidth)
    r3Label = QLabel("Settings:")
    r3Label.setMaximumWidth(labelWidth)

    row = 0
    # print(f"row: {row}")
    graphOptions.addWidget(r0Label,                        row, 0)
    graphOptions.addWidget(QLabel("Min Energy [keV]"),     row, 1)
    graphOptions.addWidget(QLabel("Max Energy [keV]"),     row, 2)
    graphOptions.addWidget(QLabel("Channels"),             row, 3)
    graphOptions.addWidget(QLabel("Counts"),               row, 4)
    graphOptions.addWidget(QLabel(""),                     row, 5)
    graphOptions.addWidget(QLabel(""),                     row, 6)

    row = 1
    # print(f"row: {row}")
    graphOptions.addWidget(r1Label,                        row, 0)
    graphOptions.addWidget(g.spectroLeftClipBox,           row, 1)
    graphOptions.addWidget(g.spectroRightClipBox,          row, 2)
    graphOptions.addWidget(g.channelNumbers,               row, 3)
    graphOptions.addWidget(g.countNumbers,                 row, 4)
    graphOptions.addWidget(ClipEnergyButton,               row, 5)
    graphOptions.addWidget(ResetClipButton,                row, 6)

    row = 2
    # print(f"row: {row}")
    graphOptions.addWidget(r2Label,                        row, 0)
    graphOptions.addWidget(g.spectroLeftFitBox,            row, 1)
    graphOptions.addWidget(g.spectroRightFitBox,           row, 2)
    graphOptions.addWidget(g.channelFitNumbers,            row, 3)
    graphOptions.addWidget(g.countFitNumbers,              row, 4)
    graphOptions.addWidget(FitButton,                      row, 5)
    graphOptions.addWidget(ResetFitButton,                 row, 6)

    row = 3
    # print(f"row: {row}")
    graphOptions.addWidget(r3Label,                        row, 0)
    # graphOptions.addWidget(QLabel("Channels to Cum:"),     row, 1)
    graphOptions.addWidget(QLabel("Cum. Channels:"),     row, 1)
    graphOptions.addLayout(cumstuff,                       row, 2)
    graphOptions.addWidget(cumChannels,                    row, 3)
    # # col 4 is empty
    graphOptions.addWidget(GammaLinesButton,               row, 5)
    graphOptions.addWidget(CalibPeakButton,                row, 6)

    ### Left side
    # Layout Calc for Gamma energies
    GammaEditBoxWidth = 60

    c1Label = QLabel("Energies [keV]:")
    c1Label.setFont(g.fatfont)

    # Editbox for Gamma
    def getComptonCalcs():
        """get Compton edge and delta from Gamma: K-40: 1460.81 --> C:1243 (DC:217)"""

        try:    g.spectroGamma4Compton = float(g.spectroGammaEditBox.text().strip().replace(",", "."))
        except: g.spectroGamma4Compton = 0
        CmptnEdge       = getComptonEdge(g.spectroGamma4Compton)
        CmptnEdgeTxt    = f"{CmptnEdge:0.2f}"                          if g.spectroGamma4Compton >  0    else "---"
        CmptnDeltaTxt   = f"{g.spectroGamma4Compton - CmptnEdge:0.2f}" if g.spectroGamma4Compton >  0    else "---"
        SingleEscapeTxt = f"{g.spectroGamma4Compton - 511:0.2f}"       if g.spectroGamma4Compton >= 1022 else "---"
        DoubleEscapeTxt = f"{g.spectroGamma4Compton - 2 * 511:0.2f}"   if g.spectroGamma4Compton >= 1022 else "---"
        g.spectroCmptnEdgResult.setText(CmptnEdgeTxt)
        g.spectroCmptnEdgDelta .setText(CmptnDeltaTxt)
        g.spectroSingleEscape  .setText(SingleEscapeTxt)
        g.spectroDoubleEscape  .setText(DoubleEscapeTxt)

    g.spectroGammaEditBox = QLineEdit()
    g.spectroGammaEditBox.setToolTip("The Gamma energy for which you want to get the Compton Edge energy")
    if g.spectroGamma4Compton != 0: g.spectroGammaEditBox.setText(f"{g.spectroGamma4Compton:0.6g}")
    else:                           g.spectroGammaEditBox.setText("")
    g.spectroGammaEditBox.setMaximumWidth(GammaEditBoxWidth)
    g.spectroGammaEditBox.textChanged.connect(lambda:  getComptonCalcs())

    # Compton Edge
    CmptnEdge  = getComptonEdge(g.spectroGamma4Compton)
    g.spectroCmptnEdgResult = QLineEdit()
    g.spectroCmptnEdgResult.setReadOnly(True)
    g.spectroCmptnEdgResult.setToolTip("The Compton Edge energy [keV] for given Gamma\ncalculated by: Gamma * (1 - 1 / (1 + 2 * Gamma / 511))")
    if g.spectroGamma4Compton > 0: g.spectroCmptnEdgResult.setText(f"{CmptnEdge:0.2f}")
    else:                          g.spectroCmptnEdgResult.setText(f"---")
    g.spectroCmptnEdgResult.setMaximumWidth(GammaEditBoxWidth)
    g.spectroCmptnEdgResult.setStyleSheet("background-color:#eee;")

    # Backscatter
    CmptnDelta = g.spectroGamma4Compton - CmptnEdge
    g.spectroCmptnEdgDelta = QLineEdit()
    g.spectroCmptnEdgDelta.setReadOnly(True)
    g.spectroCmptnEdgDelta.setToolTip("Backscatter_ max; the Delta between Gamma energy and its Compton Edge energy [keV]")
    if g.spectroGamma4Compton > 0: g.spectroCmptnEdgDelta.setText(f"{CmptnDelta:0.2f}")
    else:                          g.spectroCmptnEdgDelta.setText(f"---")
    g.spectroCmptnEdgDelta.setMaximumWidth(GammaEditBoxWidth)
    g.spectroCmptnEdgDelta.setStyleSheet("background-color:#eee;")

    # Single Escape
    SingleEscape = g.spectroGamma4Compton - 511
    g.spectroSingleEscape = QLineEdit()
    g.spectroSingleEscape.setReadOnly(True)
    g.spectroSingleEscape.setToolTip("The Single Escape of an 511keV Gamma [keV]")
    if g.spectroGamma4Compton >= 1022: g.spectroSingleEscape.setText(f"{SingleEscape:0.2f}")
    else:                              g.spectroSingleEscape.setText(f"---")
    g.spectroSingleEscape.setMaximumWidth(GammaEditBoxWidth)
    g.spectroSingleEscape.setStyleSheet("background-color:#eee;")

    # Double Escape
    DoubleEscape = g.spectroGamma4Compton - 1022
    g.spectroDoubleEscape = QLineEdit()
    g.spectroDoubleEscape.setReadOnly(True)
    g.spectroDoubleEscape.setToolTip("The Double Escape of an 2 x 511keV Gamma [keV]")
    if g.spectroGamma4Compton >= 1022: g.spectroDoubleEscape.setText(f"{SingleEscape:0.2f}")
    else:                              g.spectroDoubleEscape.setText(f"---")
    g.spectroDoubleEscape.setMaximumWidth(GammaEditBoxWidth)
    g.spectroDoubleEscape.setStyleSheet("background-color:#eee;")


    layoutComptonH = QHBoxLayout()
    layoutComptonH.addWidget(c1Label)
    layoutComptonH.addWidget(QLabel("Gamma:"))
    layoutComptonH.addWidget(g.spectroGammaEditBox)
    layoutComptonH.addStretch()
    layoutComptonH.addWidget(QLabel("Compton Edge:"))
    layoutComptonH.addWidget(g.spectroCmptnEdgResult)
    layoutComptonH.addWidget(QLabel("Back Scatter:"))
    layoutComptonH.addWidget(g.spectroCmptnEdgDelta)

    layoutComptonH2 = QHBoxLayout()
    layoutComptonH2.addWidget(QLabel("      "))
    layoutComptonH2.addStretch()
    layoutComptonH2.addWidget(QLabel("Single Escape:"))
    layoutComptonH2.addWidget(g.spectroSingleEscape)
    layoutComptonH2.addWidget(QLabel(" Dble Escape:"))
    layoutComptonH2.addWidget(g.spectroDoubleEscape)


# the fit data and other info
    g.spectroNotePad = QTextEdit()
    g.spectroNotePad.setReadOnly(True)
    g.spectroNotePad.setFont          (g.fontstd)
    g.spectroNotePad.setLineWrapMode  (QTextEdit.LineWrapMode.NoWrap) # Alts: (QTextEdit.LineWrapMode.NoWrap), QTextEdit.LineWrapMode.WidgetWidth
    g.spectroNotePad.setMinimumWidth  (500)
    g.spectroNotePad.setText          (g.spectroNotePad.toPlainText())
    g.spectroNotePad.moveCursor       (QTextCursor.MoveOperation.End)


# the dialog
    dlg = QDialog()
    g.spectroPlotPointer = dlg
    dlg.setWindowIcon         (g.iconGeigerLog)
    dlg.setWindowTitle        (f"Spectro Graph: '{g.spectroDBPath}'")
    dlg.setWindowModality     (Qt.WindowModality.WindowModal)   # can click multiple times for new graphs
    dlg.setMinimumWidth(1350)

# make bottom buttons
    CloseButton = QPushButton("Close")
    CloseButton.setAutoDefault(False)
    CloseButton.setToolTip("Close this graph window")
    CloseButton.clicked.connect(lambda:  dlg.done(0))

    ResetButton = QPushButton("Reset")
    ResetButton.setStyleSheet("QPushButton")
    ResetButton.setAutoDefault(False)
    ResetButton.setToolTip("Reset all settings to default")
    ResetButton.clicked.connect(lambda:  dlg.done(3))

    SaveButton = QPushButton("Save Graph")
    SaveButton.setStyleSheet("QPushButton")
    SaveButton.setAutoDefault(False)
    SaveButton.setToolTip("Save current graph as png-file")
    SaveButton.clicked.connect(lambda:  saveSpectroGraph())

    # add bottom buttons
    bbox = QDialogButtonBox()
    bbox.addButton(SaveButton,          QDialogButtonBox.ButtonRole.ActionRole)
    bbox.addButton(ResetButton,         QDialogButtonBox.ButtonRole.ActionRole)
    bbox.addButton(CloseButton,         QDialogButtonBox.ButtonRole.ActionRole)

    # left side
    NLabel = QLabel("NotePad:")
    NLabel.setFont(g.fatfont)

    ClearButton = QPushButton("Clear")
    ClearButton.setStyleSheet("QPushButton")
    ClearButton.setAutoDefault(False)
    ClearButton.setToolTip("Clear the NotePad")
    ClearButton.clicked.connect(lambda:  clearNotePad())

    DataButton = QPushButton("Graph-Data")
    DataButton.setAutoDefault(False)
    DataButton.setToolTip("Print database data into Spectro NotePad")
    DataButton.clicked.connect(lambda:  printSpectroData())

    InfoButton = QPushButton("Info")
    InfoButton.setAutoDefault(False)
    InfoButton.setToolTip("Print Spectro database Metadata into Spectro NotePad")
    InfoButton.clicked.connect(lambda:  printSpectroInfo())

    def save2File():
        nptxt = g.spectroNotePad.toPlainText()
        fname = g.spectroDBPath + ".nptxt"
        with (open(fname, "w") as npfile):
            npfile.write(nptxt)
        sprint(header("Saving Notepad"))
        sprint(f"to file: {fname}\n")

    SavePadButton = QPushButton("Save")
    SavePadButton.setAutoDefault(False)
    SavePadButton.setToolTip("Save Spectro NotePad to File")
    SavePadButton.clicked.connect(lambda:  save2File())


    def print2Printer():
        """Print content of Spectro Notebook to a hardware printer"""

        defname = "print2Printer: "

        defaultOutputFile = os.path.join(g.dataDir, "SpectroNotePad.pdf")

        myprinter = QPrinter()
        myprinter.  setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        myprinter.  setOutputFileName(defaultOutputFile)

        printdialog = QPrintDialog(myprinter)
        printdialog.setOption(QAbstractPrintDialog.PrintDialogOption.PrintToFile, on=True)

        if printdialog.exec():
            mydoc = g.spectroNotePad.document()
            mydoc.print(printdialog.printer())

    PrintButton = QPushButton("Print")
    PrintButton.setAutoDefault(False)
    PrintButton.setToolTip("Print Spectro NotePad to Printer")
    PrintButton.clicked.connect(lambda:  print2Printer())

    NPLayout = QHBoxLayout()
    NPLayout.addWidget(NLabel)
    NPLayout.addWidget(PrintButton)
    NPLayout.addStretch()
    NPLayout.addWidget(SavePadButton)
    NPLayout.addStretch()
    NPLayout.addWidget(DataButton)
    NPLayout.addStretch()
    NPLayout.addWidget(InfoButton)
    NPLayout.addStretch(1000)
    NPLayout.addWidget(ClearButton)

    hlinedB1 = QFrame()
    hlinedB1.setFrameShape(QFrame.Shape.HLine)

    layoutVL = QVBoxLayout()
    # layoutVL.addItem(QSpacerItem(0, 10))      # spacer
    # layoutVL.addWidget(hlinedB1)
    layoutVL.addLayout(NPLayout)                # Notepad buttons
    layoutVL.addWidget(g.spectroNotePad)        # NotePad space
    layoutVL.addLayout(layoutComptonH)          # Compton Calc 1.row
    layoutVL.addLayout(layoutComptonH2)         # Compton Calc 2. row


    SpectroPosition = QLineEdit()
    SpectroPosition.setReadOnly(True)
    SpectroPosition.setFixedWidth(200)
    SpectroPosition.setStyleSheet("background-color:#EEEEEC;")
    SpectroPosition.setAlignment(Qt.AlignmentFlag.AlignHCenter)
    SpectroPosition.setText("Cursor Position")

    # prepare the graph
    plt.close(g.spectroGraphFigno)
    g.figSpectro = plt.figure(g.spectroGraphFigno, facecolor="#C9F9F0", dpi=g.hidpiScaleMPL)                   # blueish tint
    plt.subplots_adjust(hspace=None, wspace=.2 , left=.125, top=0.88, bottom=0.11, right=.9)


    def setCanvasFocus(event):
        """Canvas gets focus when mouse hovers over the figure"""
        g.canvasSpectro.setFocus()
        # sprint(defname + f"Focus set on Canvas as event: {event.name}  {event.x}  {event.y}  {event.xdata}  {event.ydata}  {event.modifiers}  ")


    def updateSpectroCursorPos(event):
        """when cursor inside plot, get position and print to statusbar"""

        defname = "updateSpectroCursorPos: "

        try: # results in non-breaking error messages when no data are displayed
            if event.inaxes:
                # irdprint(f"{event}")
                x  = event.x
                y  = event.y
                xd = event.xdata
                yd = event.ydata

                ydata = event.ydata
                ylBot, ylTop = sax1.get_ylim()
                yrBot, yrTop = sax2.get_ylim()
                yleft = (ydata - yrBot) / (yrTop - yrBot) * (ylTop - ylBot) + ylBot
                # rdprint(defname, f"updatecursorposition: x:{x:0.10f} y1:{y1:0.3f}  y2:{y2:0.3f}")

                ch = customformat(xd,       5, 1, thousand=False)
                cn = customformat(yleft,    5, 1, thousand=False)
                wd = customformat(yd,       5, 1, thousand=False)
                SpectroPosition.setText(f" E:{ch} C:{cn} W:{wd}")
            else:
                # SpectroPosition.setText("Cursor Position")
                SpectroPosition.setText("Mouse Position on Graph")

        except Exception as e:
            exceptPrint(e, defname)


    g.canvasSpectro = FigureCanvas(g.figSpectro)
    g.canvasSpectro.setMinimumHeight(500)
    g.canvasSpectro.mpl_connect('button_press_event',  onSpectroClick)          # send a mouse button click event
    g.canvasSpectro.mpl_connect('figure_enter_event',  setCanvasFocus)          # sent when the mouse cursor enters the figure
    g.canvasSpectro.mpl_connect('motion_notify_event', updateSpectroCursorPos)  # send a mouse move event

    # my Stretch
    CustomStretch = QWidget()
    CustomStretch.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    # Toolbar Spectro
    g.spectroToolbar = QToolBar("Spectro Toolbar")

    g.spectroToolbar.addWidget(g.checkFit)
    # g.spectroToolbar.addWidget(g.checkSearchPeaks)
    g.spectroToolbar.addWidget(checkShowChnlW)
    g.spectroToolbar.addWidget(checkShowOrig)
    g.spectroToolbar.addWidget(CustomStretch)
    g.spectroToolbar.addWidget(checkShowGrid)
    g.spectroToolbar.addWidget(checkShowLine)
    g.spectroToolbar.addWidget(checkShowLog)
    g.spectroToolbar.addWidget(SpectroPosition)


    # left side
    layoutVR = QVBoxLayout()
    layoutVR.addLayout(graphOptions)
    layoutVR.addWidget(g.spectroToolbar)
    layoutVR.addWidget(g.canvasSpectro, stretch=1000)

    # combine Layouts left and right
    layoutH = QHBoxLayout()
    layoutH.addLayout(layoutVL, 45)
    layoutH.addLayout(layoutVR, 55)

    # Main Layout - add buttons
    layoutVMain = QVBoxLayout()
    layoutVMain.addLayout(layoutH)
    layoutVMain.addWidget(bbox)

    dlg.setLayout(layoutVMain)

    # prepare the data to be used in plot
    if reset: printSpectroInfo()

    updateEditBoxes()
    makeFitPeak()
    updateEditBoxes()
    plotGraphSpectro()

    # show window
    retval = dlg.exec()
    dprint(defname, "retval: ", retval)

#ret - evaluate response actions
    rflag = False

    # close - the only EXIT
    if retval == 0:
        gdprint(defname, "'CLOSE' called")
        plt.close(g.spectroGraphFigno)                               # closes the figure
        g.figSpectro = None
        return

    # clip and clipFit
    elif retval == 1:
        gdprint(defname, "DONE(1) called #####################################################################################")
        fillEnergyBoxes()   # nur benutztt nach manueller Zahleneingabe

    # reset
    elif retval == 3:
        gdprint(defname, "RESET called")
        rflag = True
        resetSpectroParams()

    # cumulative
    elif retval == 7:
        gdprint(defname, "CUMUL called")
        try:    cumul = clamp(int(float(cumvalue.text().strip().replace(",", "."))), 1, 100)
        except: cumul = 1
        g.spectroCumul = cumul

    # cleanup before restarting
    plt.close(g.spectroGraphFigno)                           # closes the figure
    g.figSpectro = None
    initSpectroGraph(reset=rflag)           # re-plot Spectro without resetting


def fillEnergyBoxes():

    defname = "fillEnergyBoxes: "

    if g.spectroLeftClipBox is None: return

    rdprint(defname, "g.spectroMax ", g.spectroMaxE, "  g.spectroMin ", g.spectroMinE)

    # clip-energy
    # left
    try:    g.spectroLeftClipEnergy  = clamp(float(g.spectroLeftClipBox .text().strip().replace(",", "")), g.spectroMinE, g.spectroMaxE)
    except Exception as e:
        exceptPrint(e, defname)
        g.spectroLeftClipEnergy  = g.spectroMinE

    # right
    try:    g.spectroRightClipEnergy = clamp(float(g.spectroRightClipBox.text().strip().replace(",", "")), g.spectroMinE, g.spectroMaxE)
    except Exception as e:
        exceptPrint(e, defname)
        g.spectroRightClipEnergy = g.spectroMaxE


    # fit-energy
    # left
    try:    g.spectroLeftFitEnergy   = clamp(float(g.spectroLeftFitBox .text().strip().replace(",", "")), g.spectroMinE, g.spectroMaxE)
    except Exception as e:
        exceptPrint(e, defname)
        g.spectroLeftFitEnergy   = g.spectroMinE

    # right
    try:    g.spectroRightFitEnergy  = clamp(float(g.spectroRightFitBox.text().strip().replace(",", "")), g.spectroMinE, g.spectroMaxE)
    except Exception as e:
        exceptPrint(e, defname)
        g.spectroRightFitEnergy  = g.spectroMaxE


#
# get a spectro file
#
#file
def getFileSpectro(defaultSpectroDBPath=None, source="Database", restart=True, quiet=False):
    """Load either spectro or other file 'standard'"""

    ####### begin local def ########################################################################################

    ### get Calib coeffs
    def getCoeffsFromComments(com):
        """get Coeffs from comments"""

        try:
            CalScale = (com.strip().split(":")[-1]).strip("[] ")
        except Exception as e:
            exceptPrint(e, f"{'Calibration Scale':20s}: Failure: Setting: {com}")
            success = False
        else:
            for i, cs in enumerate(CalScale.split(",")):
                try:
                    val = float(cs)
                    if abs(val) < 0.01 / 1E4**i: val = 0.0
                except Exception as e:
                    exceptPrint(e, "Getting coefficients from comments")
                    success = False
                    break
                g.spectroScaleOrig[i] = val
                success = True

        return success


    #### get spectrum
    def getSpectroDataFromSpectroFile(fromPath):
        """Uses numpy command to load data from CSV into in-memory np.array"""

        defname = gd(sys._getframe().f_code.co_name)

        cdprint(defname, f"fromPath: {fromPath}")

        csvdata                = np.empty((0, 2))      # empty data; two columns
        g.spectroCommentsOrg   = []                    # reset META comments; each item in this list ends WITHOUT LF
        g.spectroCommentsGlg   = []                    # reset GL comments; each item in this list ends WITHOUT LF

        ### assemble all comments from CSV file into g.spectroCommentsOrg and spectroCommentsGlg as list
        try:
            with (open(fromPath, "r") as rawfile):
                rawlines = rawfile.readlines()          # type rawlines: <class 'list'>  rawlines[i]: e.g.:  b'0.46,2\n'
        except Exception as e:
            exceptPrint(e, defname + "cannot read CSV file")
            return csvdata
        else:
            try:
                for rawline in rawlines:
                    rawline = rawline.strip()
                    if rawline == "": continue
                    if rawline[0] == "#":                                                     # lines beginning with '#' are always comments
                        if rawline.startswith("#G"): g.spectroCommentsGlg.append(rawline)     # GeigerLog Meta
                        else:                        g.spectroCommentsOrg.append(rawline)     # original Meta
            except Exception as e:
                exceptPrint(e, defname + "Failed while reading comments")
                return csvdata

        # screen the Meta comments
        for com in g.spectroCommentsOrg:
            cdprint(defname, f"Comment:  {com[0:200]}")
            if "Calibration" in com:
                if not getCoeffsFromComments(com): return csvdata


        # screen the GeigerLog comments
        for com in g.spectroCommentsGlg:
            cdprint(defname, f"Comment:  {com[0:200]}")
            if "Calibration" in com:
                if not getCoeffsFromComments(com): return csvdata

        # now get the CSV data by numpy np.genfromtxt into csvdata  -  type(csvdata): <class 'numpy.ndarray'>, csvdata.shap (1928, 2)
        try:
            csvdata = np.genfromtxt(rawlines, delimiter=",", comments="#", filling_values=g.NAN)
            cdprint(defname, f"Return:   csvdata: shape: {csvdata.shape}   typ {type(csvdata)}")
        except Exception as e:
            exceptPrint(e, defname + "Failed reading data from: " + fromPath)

        return csvdata


#csv
    def saveSpectroCSVFile(fromPath, toPath):
        """Read the CSV File and set the '#' char in front of any comment; write file with '.spectro' extension"""

        # defname = "saveSpectroCSVFil "
        defname = gd(sys._getframe().f_code.co_name)

        # cdprint(defname, f"sourc {source}, fromPath: {fromPath}")
        # cdprint(defname, f"sourc {source}, toPath:   {toPath}")

        ssCSVstart = time.time()

        # read the csv file
        try:
            with (open(fromPath, "r") as rawfile): rawlines = rawfile.readlines()           # type rawlines: <class 'list'>  rl[1]: b'0.46,2\n'
        except Exception as e:
            exceptPrint(e, defname + f"cannot read CSV file '{fromPath}'")
        else:
            # cdprint(defname, "type rawlines: ", type(rawlines), "  rl[1]: ", bytes(rawlines[1], "utf-8"))
            # mdprint(defname, f"Reading Finished in {time.time() - ssCSVstart:0.3f} sec")

            try:                                                                        # write the database-csv file
                with (open(toPath, "w") as spectrofile):

                    if   source == "CSV-SPE":
                        ### fit to the SPE datacurve
                        # p3 = 1.5258E-07     # x³
                        # p2 = 8.8478E-05     # x²
                        # p1 = 1.4257E+00     # x
                        # p0 = 4.5645E-01     # const
                        spectrofile.write(f"#G {'File Type'          }::CSV-SPE\n")
                        spectrofile.write(f"#G {'Detector Type'      }::CsI\n")
                        spectrofile.write(f"#G {'Manufacturer'       }::Deepace (https://deepace.net/)\n")
                        spectrofile.write(f"#G {'Device'             }::MEASALL KC761B\n")

                    elif source == "CSV-MC":
                        # Files is CSV with: <chnlNumber>, <counts>
                        spectrofile.write(f"#G {'File Type'          }::CSV-MC\n")
                        spectrofile.write(f"#G {'Detector Type'      }::CsI\n")
                        spectrofile.write(f"#G {'Manufacturer'       }::Deepace (https://deepace.net/)\n")
                        spectrofile.write(f"#G {'Device'             }::MEASALL KC761B\n")
                        # spectrofile.write(f"#G {'Orig. Calib. Coeffs'}::{[0, 1, 0, 0]}\n")

                    elif source == "CSV-GEN":
                        # any generic 1 or 2-column CSV file
                        spectrofile.write(f"#G {'File Type'          }::Generic CSV\n")
                        spectrofile.write(f"#G {'Detector Type'      }::Unknown\n")
                        spectrofile.write(f"#G {'Manufacturer'       }::Unknown\n")
                        spectrofile.write(f"#G {'Device'             }::Unknown\n")

                    elif source == "CANBERRA-TKA":
                        # Der BEGE Detektor ist ein Broad Energy Germanium Detektor mit einem Carbon Endkappenfenster. Er misst bis
                        # ca 2KeV herunter ;), Übliche HPGe-Detektoren messen erst ab 40keV (können aber u. Umständen je nach Detektor
                        # bei schlechterer Effizienz auch noch Signale von etwa 27keV "sehen". Laut Mirion misst er von 3keV bis 3MeV.
                        # Hersteller : Mirion/Canberra,  Preis: rund 68 T€
                        # https://www.mirion.com/de/products/technologies/spectroscopy-scientific-analysis/gamma-spectroscopy/detectors/hpge-detectors-accessories/bege-broad-energy-germanium-detectors
                        # EXAMPLE Code for .CNF files:  https://assets-mirion.mirion.com/prod-20220822/cms4_mirion/files/pdf/landing-pages/genie-4-python/genie-python-sdk-examples.pdf
                        #
                        # from:  #3 in https://www.geigerzaehlerforum.de/index.php?topic=1440.0
                        # "bei der .TKA Datei habe ich das "Gefühl", genau weiß ich es aber nicht, das die ersten zwei Einträge die Messzeit
                        # betreffen (Lifetime und Realtime) und nicht den Kanalinhalten zugeordnet werden. Zumindest beim Import in Excel sieht das so aus."
                        # NOTE: TKA is simple file format with one number on each line:
                        # first 2 line are NOT count data
                        #   Line 1:  Live time
                        #   Line 2:  Real time
                        #   Line 3:  counts first channel
                        #   ...
                        #   Line N:  counts last channel
                        #
                        # Coefficients genommen von Canberra CNF files
                        spectrofile.write(f"#G {'File Type'          }::CANBERRA-TKA\n")
                        spectrofile.write(f"#G {'Detector Type'      }::BEGe (Broad Energy Germanium) Detector\n")
                        spectrofile.write(f"#G {'Manufacturer'       }::Mirion / Canberra (https://www.mirion.com/de)\n")
                        spectrofile.write(f"#G {'Device'             }::Unknown\n")
                        spectrofile.write(f"#G {'Orig. Calib. Coeffs'}::{[-0.073745, 0.229648,  0.,        0.,      ]}\n")

                    else:
                        spectrofile.write(f"#G {'File Type'          }::Generic CSV\n")
                        spectrofile.write(f"#G {'Detector Type'      }::Unknown\n")
                        spectrofile.write(f"#G {'Manufacturer'       }::Unknown\n")
                        spectrofile.write(f"#G {'Device'             }::Unknown\n")


                    # COMMENTS: first find any comments and assemble them
                    comlines = []
                    for i, rawline in enumerate(rawlines):
                        rawline  = rawline.strip()
                        # cdprint(defname, f"rawlin '{rawline}'")

                        if   rawline == "":         continue                            # empty line
                        elif rawline[0].isdigit():  continue                            # this is data; ignore for now
                        elif rawline[0] == "#":     comlines.append(rawline)            # already marked as comment
                        else:                       comlines.append("#M " + rawline)     # line begins with non-digit; make to a comment
                    # mdprint(defname, f"Comments Finished in {time.time() - ssCSVstart:0.3f} sec")

                    # DATA: comments are done, now find data
                    datalines  = []
                    TwoColumns = False
                    for i, rawline in enumerate(rawlines):
                        rawline  = rawline.strip()
                        # cdprint(defname, f"rawlin '{rawline}'")

                        if   rawline == "":             continue                            # empty line
                        elif not rawline[0].isdigit():  continue                            # this is NOT data; ignore for now
                        else:  # here are data
                            newline = rawline.strip().rstrip(",").replace(" ", "")                  # remove ',' at the end, and change " " to ""
                            if source == "CANBERRA-TKA":
                                # Calibration using coefficients from CNF file: [-0.073745  0.229648  0.        0.      ]
                                TwoColumns = False                                          # energy is already calculated from Calib Coeff
                                # make first 2 lines to comments
                                if   i >= 2: datalines.append("{:>9.4f}, {}".format(-0.073745 + 0.229648 * i, newline))
                                elif i == 0: comlines .append(f"# {'Live time'}::{rawline}")
                                elif i == 1: comlines .append(f"# {'Real time'}::{newline}")

                            elif source == "CSV-SPE":
                                # has 2-data columns, first is energy
                                TwoColumns = True
                                datalines.append(newline)

                            elif source == "CSV-MC":
                                # has 2-data columns, but first is channel anyway
                                TwoColumns = False
                                datalines.append(newline)

                            elif source == "CSV-GEN":
                                # can handle 1 or 2-data columns
                                irdprint(defname, f"newline: {newline}")
                                newline = newline.strip()
                                newlineList = newline.split(",", maxsplit=1)                    # force max 2-col data
                                if len(newlineList) == 1:
                                    TwoColumns = False
                                    # datalines.append("{:>7s}, {}\n".format(str(i), *newlineList))
                                    datalines.append("{:>4s}, {}".format(str(i), *newlineList))
                                else:
                                    TwoColumns = True
                                    # datalines.append("{:>7s}, {}\n".format(*newlineList))
                                    datalines.append("{:>4s}, {}".format(*newlineList))

                            else:
                                # can handle 1 or 2-data columns
                                irdprint(defname, f"newline: {newline}")
                                newline = newline.strip()
                                irdprint(defname, f"newline: {newline}")
                                newlineList = newline.split(",", maxsplit=1)                    # force max 2-col data
                                if len(newlineList) == 1:
                                    TwoColumns = False
                                    datalines.append("{:>4s}, {}\n".format(str(i), *newlineList))
                                else:
                                    TwoColumns = True
                                    datalines.append("{:>4s}, {}\n".format(*newlineList))

                    # mdprint(defname, f"Data Finished in {time.time() - ssCSVstart:0.3f} sec")

                    if TwoColumns:
                        irdprint(defname, f"TwoColumns: ")
                        if len(datalines) == 0:
                            efprint(f"Found an empty datafile {fromPath}  - cannot process further")
                            return

                        npdatalines       = np.full(len(datalines), g.NAN)
                        for i, dl in enumerate(datalines):
                            x, y = dl.split(",")
                            try:
                                npdatalines[i] = float(x)
                            except Exception as e:
                                exceptPrint(e, defname + f"Can't convert CSV value '{x}' to Float")
                                npdatalines[i] = g.NAN

                        g.spectroScale  = getFitEnergyCalib(npdatalines, verbose=False)    # verbose MUST be False when called from main, because Snotepad is not defined
                        sS              = ", ".join(f"{gss:0.9g}" for gss in g.spectroScale)
                        comlines.append(f"#G {'GeigerLog Calibration' }::[{sS}]\n")
                        # mdprint(defname, f"Two columns Finished in {time.time() - ssCSVstart:0.3f} sec")

                    else:   # single column
                        spectrofile.write(f"#G {'GeigerLog Calibration'}::{[0, 1, 0, 0]}\n")
                        # mdprint(defname, f"Single column Finished in {time.time() - ssCSVstart:0.3f} sec")

                    for com  in comlines:    spectrofile.write(com  + "\n")
                    for data in datalines:   spectrofile.write(data + "\n")
                    # mdprint(defname, f"Re-Writing Finished in {time.time() - ssCSVstart:0.3f} sec")

            except Exception as e:
                exceptPrint(e, defname + "writing spectro file")

        mdprint(defname, f"Finished in {time.time() - ssCSVstart:0.3f} sec")


#csv HDS101
    def saveSpectroHDS101CSVFile(fromPath, toPath):
        """Read the CSV File from device HDS101G and set the '#' char in front of any comment; write file with '.spectro' extension"""

        defname = "saveSpectroHDS101CSVFil "

        # read the file
        try:
            with (open(fromPath, "r") as rawfile): rawlines = rawfile.readlines()           # type rawlines: <class 'list'>  rl[1]: b'0.46,2\n'
        except Exception as e:
            exceptPrint(e, defname + f"cannot read CSV file '{fromPath}'")
        else:
            # cdprint(defname, "type rawlines: ", type(rawlines), ", type rawlines[0]: ", type(rawlines[0]), "  bytes(rl[1]): ", bytes(rawlines[1], "utf-8"))

            try:                                                                        # write the database-csv file
                with (open(toPath, "w") as spectrofile):
                    spectrofile.write(f"#G {'File Type'     }::HDS101-CSV-SPE\n")
                    spectrofile.write(f"#G {'Detector Type' }::CsI\n")
                    spectrofile.write(f"#G {'Manufacturer'  }::MGP INSTRUMENTS HDS\n")
                    spectrofile.write(f"#G {'Device'        }::HDS101G\n")

                    newline     = ""
                    iline       = 0
                    datapointer = 0
                    offset      = 0.0       # will be overwritten
                    scale       = 1.0       # will be overwritten
                    start, stop = 0, 511    # will be overwritten
                    while True:
                        rawline  = rawlines[iline].strip().lstrip("$").rstrip(":")      # convert from: '$SPEC_REM:'  to: 'SPEC_REM'
                        # mdprint(defname, f"rawline: {rawline}")

                        if rawline == "":
                            iline   += 1

                        else:
                            newline += f"#M {rawline}::"
                            iline   += 1
                            newline += " " + rawlines[iline].strip()

                            if rawline == "SPEC_REM":         # 2 comments coming; combine both on single line
                                iline   += 1
                                newline += ", " + rawlines[iline].strip()

                            elif rawline == "DATE_MEA":
                                pass

                            elif rawline == "MEAS_TIM":
                                pass

                            elif rawline == "ENER_FIT":
                                offset, scale   = (rawlines[iline].strip()).split()
                                offset          = float(offset)
                                scale           = float(scale)
                                g.spectroScale  = [offset, scale, 0, 0]
                                newline        += f"\n#G {'Internal Calibration'}::{g.spectroScale}"

                            elif rawline == "GAIN_OFFSET_XIA":
                                pass

                            elif rawline == "TEMPERATURE":
                                pass

                            elif rawline == "MGP_DEVICE_ID":
                                pass

                            elif rawline == "MGP_SPEC_ID":
                                pass

                            elif rawline == "DATA":
                                nextline = rawlines[iline].strip()  # get the channel limits, like: '0 511'
                                start, stop = nextline.split(" ")
                                start       = int(start)
                                stop        = int(stop)
                                cdprint(defname, f"newline: # Data: start: {start}   stop: {stop}")

                                datapointer = iline
                                iline += stop - start + 1

                            else:
                                newline = ""

                            if newline > "":
                                cdprint(defname, f"newline: {newline}")
                                spectrofile.write(newline + "\n")
                                newline = ""

                            iline   += 1
                            if iline >= len(rawlines) : break

                    iline = datapointer
                    for i in range(start, stop + 1):
                        iline  += 1
                        energy  = offset + scale * i
                        newline = f"{energy:9.4f}, {rawlines[iline].strip()}"
                        # cdprint(defname, f"newline: {newline}")
                        spectrofile.write(newline + "\n")

            except Exception as e:
                exceptPrint(e, defname)


#cnf
    def saveSpectroCNFFile(fromPath, toPath):
        """Read a CNF File and save content as Spectrro CSV File"""

        defname = "saveSpectroCNFFile: "

        ### read file via converter
        cnfcontent  = gsup_spectro_cnf.read_cnf_file(fromPath, write_output=False)  # "write_output=True" gets a file with ext=text with Dict data
        ###
        ### cnfcontent is Canberra dict like this:
        # Energy coefficients  [-0.073745  0.229648  0.        0.      ]
        # Energy unit          keV
        # MCA type             DSA-LX
        # Data source          DET02
        # Real time            319.66969689999996
        # Live time            299.9999999
        # Start time           07-03-2025, 15:35:17
        # Shape coefficients   [0.391178 0.037631 0.       0.      ]
        # Left marker          20
        # Right marker         50
        # Sample name          Sample titel
        # Sample id
        # Sample type
        # Sample units         Unit
        # Sample geometry
        # User name            Physik Ha
        # Sample description   9 Ringe plus 3D-Druckanpassung+Ringaufsatz   +Plexiglas-Schale da Aufsatz mit Loch
        # Number of channels   8192
        # Channels data        [  0   0   0   3 210 ...   0   0   0   0   0]
        # Channels             [   1    2    3    4    5 ... 8188 8189 8190 8191 8192]              # !!! channels starts with '1', not '0' !!!
        # Total counts         568563
        # Measurement mode     PHA
        # Energy               [1.559022e-01 3.855498e-01 6.151974e-01 8.448450e-01 1.074493e+00 ... 1.880281e+03 1.880511e+03 1.880740e+03 1.880970e+03 1.881200e+03]
        # Counts in markers    7520

        N_chan          = cnfcontent["Number of channels"]
        CNFEnergy       = cnfcontent["Energy"]
        CNFCounts       = cnfcontent["Channels data"]

        E_coeff         = cnfcontent["Energy coefficients"]
        g.spectroScale  = E_coeff
        str_coeff       = "[{:0.6G}, {:0.6G}, {:0.6G}, {:0.6G}]".format(*E_coeff)

        irdprint(defname, f"type(CNFEnergy): {type(CNFEnergy)} ---------------------------------------")
        # correction: because CNF starts with channel 1, not 0(zero)!!! here: add index 0 to Energy
        CNFEnergy       = np.append(np.array([E_coeff[0]]), CNFEnergy[:-1])

        comments = []
        # contributed by GeigerLog
        comments.append(f"#G {'File Type'           }::CANBERRA-CNF")
        comments.append(f"#G {'Detector Type'       }::BEGe (Broad Energy Germanium) Detector")
        comments.append(f"#G {'Manufacturer'        }::Mirion / Canberra (https://www.mirion.com/de)")
        comments.append(f"#G {'Device'              }::Unknown")

        # contributed by CNF content
        comments.append(f"#M {'Sample id'           }::{cnfcontent['Sample id'] if cnfcontent['Sample id'] > '' else 'None'}")
        comments.append(f"#M {'Measurement mode'    }::{cnfcontent['Measurement mode']}")
        comments.append(f"#M {'Start time'          }::{cnfcontent['Start time']}")
        comments.append(f"#M {'Real time'           }::{cnfcontent['Real time']:0.2f}")
        comments.append(f"#M {'Live time'           }::{cnfcontent['Live time']:0.2f}")

        comments.append(f"#M {'MCA type'            }::{cnfcontent['MCA type']}")
        comments.append(f"#M {'Data source'         }::{cnfcontent['Data source']}")

        comments.append(f"#M {'Channels used'       }::{N_chan}")
        comments.append(f"#M {'Original Calibration'}::{str_coeff}")
        comments.append(f"#M {'Sample description'  }::{cnfcontent['Sample description']}")

        strEngy = f"{cnfcontent['Energy'][:3]}" + "..." + f"{cnfcontent['Energy'][-3:]}"
        comments.append(f"#M {'Energy'              }::{strEngy}")

        with open(toPath, "w" ) as cnffile:
            for com in comments:    cnffile.write(com + "\n")                               # write all comments to file
            for i in range(N_chan): cnffile.write(f"{CNFEnergy[i]:9.4f}, {CNFCounts[i]}\n")    # write all data to file


#xml-N42
    def saveSpectroXML_N42File(fromPath, toPath):
        """Load XML file spectro file and create DB-CSV file"""

        # NOT The DHS files come with a 'DHS:' namespace, used in the lower part of the file:
        #  <DHS:Raysid version="1">
        #   <RawCounts>43808</RawCounts>
        #   ...
        #   </Peaks>
        #  </DHS:Raysid>
        # However, this namespace is not defined and results in an error of a standard parser!
        # The remedy:
        #    1. remove the 2 occurences of 'DHS:'
        # or 2. add a nonsense definition in the top: <RadInstrumentData xmlns:DHS="http://www.w3.org/TR/html4/"  xmlns:xsi...
        # or 3. use a parser like 'lxml' for such XML files and configure for ignore errors: 'parser = etree.XMLParser(ns_clean=True, recover=True)'
        # GeigerLog uses the thrid option

        # Raysid:  https://raysid.com/


        defname = gd(sys._getframe().f_code.co_name)

        ### open spectrum file and read all lines
        with open(fromPath, "r" ) as xmlfile:
            alldata = xmlfile.readlines()           ### type(alldata) is <class 'list'>

        # getting comments
        comments = []

        # contributed by GeigerLog
        comments.append(f"G {'File Type'}::{'XML-N42'}")

        # contributed by XML content
        # this is reading an XML file - there should not be any comments! But, nevermind
        pureXML = ""
        for data in alldata:
            if data.strip()[0] == "#":  # this is a comment
                mdprint(defname, f"alldata comments: {data.rstrip()}")
                comments.append(data)
            else:
                pureXML += data     # add to string; parser needs string

        # parse the xml data string
        try:
            parser = etree.XMLParser(ns_clean=True, recover=True)           # recover allows to ignore missing DHS definition
            root   = etree.fromstring(pureXML, parser)
        except etree.ParseError as e:
             exceptPrint(e, "ParseError parsing XML file")
             efprint("Failure loading XML file!")
             return
        except Exception as e:
             exceptPrint(e, "Non-ParseError Exception parsing XML file")
             efprint("Failure loading XML file!")
             return

        if root is None:
            msg = f"File {fromPath} is not a XML document!"
            efprint(msg)
            edprint(msg)
            return []

        if len(parser.error_log) > 0: rdprint(defname, "XML Parser error log: len:", len(parser.error_log), " typ", type(parser.error_log), "error msg:\n", parser.error_log)
        else:                         gdprint(defname, "XML Parser error log: No Error")

        # g.spectroXMLroot = root
        mdprint(defname,f"len(alldata): {len(alldata)}")                # e.g. 64
        mdprint(defname, "len(root):    ", len(root))                   # 5
        mdprint(defname, "root.tag:     ", root.tag)                    # {http://physics.nist.gov/N42/2011/N42}RadInstrumentData
        mdprint(defname, "root.text:    ", "as bytes: ", bytes(root.text, "utf-8", errors='ignore'))   # <empty>; is: b'\n  '
        mdprint(defname, "root.attrib:  ", root.attrib)                 # '{http://www.w3.org/2001/XMLSchema-instance}schemaLocation': 'http://physics.nist.gov/N42/2011/N42 http://physics.nist.gov/N42/2011/n42.xsd', 'n42DocUUID': 'f3cbfdc1-03d8-4c39-ab08-b103060cc702'}

        for element in root.iter():
            # tag = element.tag.replace("{http://physics.nist.gov/N42/2011/N42}", "")
            if   "ChannelData"                   in str(element): scounts         = element.text   # the Count data per Channel
            elif "EnergyBoundaryValues"          in str(element): senergy         = element.text   # the calibration per channel
            elif "RadDetectorCategoryCode"       in str(element): RDCatCode       = element.text   # Radiation = Gamma
            elif "RadDetectorKindCode"           in str(element): RDKindCode      = element.text   # Sensor    = "CsI"
            elif "RadInstrumentModelName"        in str(element): RDModelName     = element.text   # Device    = "Raysid"
            elif "RadInstrumentComponentName"    in str(element): RIComponentName = element.text   #           = "Raysid Firmware"
            elif "RadInstrumentComponentVersion" in str(element): RIComponentVers = element.text   # Version   = "1.4.9560"
            elif "RadInstrumentManufacturerName" in str(element): RIManufName     = element.text   # IN-NEW (What is it? Maybe: Internal, New???)

        comments.append(f"M {'Institution'  }::{(root.tag).replace('{', '')}")
        comments.append(f"M {'Manufacturer' }::{RIManufName}")
        comments.append(f"M {'Detector Type'}::{RDKindCode}")
        comments.append(f"M {'Device'       }::{RDModelName}")
        comments.append(f"M {RIComponentName}::Version: {RIComponentVers}")

        counts = []
        for scount in scounts.split(" ")[:-1]:
            try:    val = float(scount)
            except  Exception as e:
                exceptPrint(e, defname + f"scount: {scount}")
                val = g.NAN
            counts.append(val)

        energy = []
        for sener in senergy.split(" ")[:-1]:
            try:    val = float(sener)
            except  Exception as e:
                exceptPrint(e, defname + f"sener: {sener}")
                val = g.NAN
            energy.append(val)

        comments.append(f"M {'Energy Boundaries'}::{energy[0:5]} ... {energy[-5:]}")

        g.spectroData = []
        for i in range(min(len(counts), len(energy))):
            g.spectroData.append([energy[i], counts[i]])                     # make g.spectroData list
        g.spectroData = np.array(g.spectroData)                              # convert to numpy array - essential for splicing !!!!!!!!!!!

        xdata  = g.spectroData[:, 0]
        popt   = getFitEnergyCalib(xdata)                                    # popt:  [ 1.716462e-06 -2.085417e-03  1.890134e+00 -1.490695e+02]
        coeffs = ", ".join(f"{lp:<.9g}" for lp in popt)

        # comments.append(f"#G {'Internal Calibration' :20s}: [{coeffs}]")
        comments.append(f"G {'Internal Calibration'}::[{coeffs}]")

        with open(toPath, "w" ) as csvfile:
            for com in comments:
                scom = com.split("::", 1)
                if len(scom) == 2:  csvfile.write(f"#{scom[0].strip():22s} :: {scom[1].strip()}\n")
                else:               csvfile.write(f"#{com}\n")

            for line in g.spectroData:
                csvfile.write(f"{line[0]:9.4f}, {line[1]}\n")

        return g.spectroData


#xml-RadiaCode
    def saveSpectroXML_RadiaCodeFile(fromPath, toPath):
        """Load XML file and create spectro file"""
        # NOTE: anders als bei DHS kein XML Fehler festegstellt

        defname = "saveSpectroXML_RadiaCodeFil "

        with open(fromPath, "r" ) as xmlfile:
            alldata = xmlfile.readlines()           ### typ <class 'list'>

        # getting comments
        comments = []

        # contributed by GeigerLog
        comments.append(f"#G {'File Type'}::XML-RadiaCode")

        # contributed by XML content
        # this is reading of an XML file - there should not be any comments! But, nevermind
        pureXML = ""
        for data in alldata:
            datastrip = data.strip()
            if datastrip == "": continue
            if datastrip[0] == "#":  # this is a comment
                mdprint(defname, f"alldata comments: {data.rstrip()}")
                comments.append(data)
            else:
                pureXML += data     # add to string; parser needs string

        # parse the xml data string
        try:
            parser = etree.XMLParser(ns_clean=True, recover=True)           # recover allows to ignore missing DHS definition
            root   = etree.fromstring(pureXML, parser)
        except etree.ParseError as e:
             exceptPrint(e, "ParseError parsing XML file")
             efprint("Failure loading XML file!")
             return
        except Exception as e:
             exceptPrint(e, "Non-ParseError Exception parsing XML file")
             efprint("Failure loading XML file!")
             return

        if len(parser.error_log) > 0: rdprint(defname, "XML Parser error log: len:", len(parser.error_log), " typ", type(parser.error_log), "error msg:\n", parser.error_log)
        else:                         gdprint(defname, "XML Parser error log: No Error")

        # g.spectroXMLroot = root
        cdprint(defname,f"len(alldata): {len(alldata)}")                                                # e.g. 1073  (lines of text)
        cdprint(defname,f"len(purexml): {len(pureXML)}")                                                # e.g. 29629 (bytes)
        cdprint(defname, "len(root):    ", len(root))                                                   # 2
        cdprint(defname, "root.tag:     ", root.tag)                                                    # ResultDataFile
        cdprint(defname, "root.text:    ", "as bytes: ", bytes(root.text, "utf-8", errors='ignore'))    # <empty>; is: b'\n  '
        cdprint(defname, "root.attrib:  ", root.attrib)                                                 # {}

        energy = []
        counts = []
        channelcount = 0
        for element in root.iter():
            tag = element.tag
            elt = element.text
            if elt is None:
                rdprint(defname,   f"element: tag: {tag:30s} :  <element.txt is None>")
            else:
                if elt == "":
                    dprint(defname,   f"element: tag: {tag:30s} :  <empty>")

                elif "ResultData" in str(tag):
                    for child in element:
                        # print(child.tag, child.attrib, child.text )
                        if   child.tag == "StartTime":  comments.append(f"#M {'Start Time'}::{child.text}")
                        elif child.tag == "EndTime":    comments.append(f"#M {'End Time'  }::{child.text}")
                        elif child.tag == "DeviceConfigReference":
                            # cdprint(defname, f"DeviceConfigReference")
                            for grandchild in child:
                                # gdprint(grandchild.tag, grandchild.attrib, grandchild.text )
                                if   grandchild.tag == "Name": comments.append(f"#M {'Device'}::{grandchild.text}")

                elif "DataPoint" in str(tag):
                    scount      = element.text                     # the 'Count' data for each Channel
                    try:    val = float(scount)
                    except  Exception as e:
                        exceptPrint(e, defname + f"scount: {scount}")
                        val = g.NAN
                    counts.append(val)
                    channelcount += 1
                    energy.append(coeffs[0] + coeffs[1] * channelcount + coeffs[2] * channelcount**2)

                # this does come BEFORE the DataPoint; so coeffs are known before datapoint energy is calulated!
                elif "EnergyCalibration" in element.tag:
                    for child in element:
                        # print(child.tag, child.attrib, child.text )
                        if child.tag == "PolynomialOrder":
                            PolyOrd = int(child.text)               # PolyOrd is == 2
                            coeffs = [g.NAN] * (PolyOrd + 1)
                        else:
                            coeffs = [g.NAN] * 3

                        if child.tag == "Coefficients":
                            for i, grandch in enumerate(child):
                                # print(grandch.tag, grandch.attrib, grandch.text )
                                coeffs[i] = float(grandch.text)

                    g.spectroScale = [*coeffs, 0]                                  # radiacode has only 3 coeffs; add the 4th for GeigerLog
                    cdprint(defname, f"Coeffs: {coeffs}")
                    cdprint(defname, f"spectroScale: {g.spectroScale}")
                    comments.append(f"#M {'Internal Calibration'}::{g.spectroScale}")

                elif "EnergySpectrum" in element.tag:
                    for child in element:
                        # print(child.tag, child.attrib, child.text )
                        if   child.tag == "MeasurementTime": comments.append(f"#M {'Measurement Time'}::{child.text:<10s} ({float(child.text) / 60 / 60 / 24:0.4f} days)")
                        elif child.tag == "LiveTime":        comments.append(f"#M {'Live Time'       }::{child.text:<10s} ({float(child.text) / 60 / 60 / 24:0.4f} days)")

                else:
                    cdprint(defname, f"element: tag: {tag:30s} :  {elt.strip()[0:100]}")

        with open(toPath, "w" ) as csvfile:
            for com in comments:
                csvfile.write(com + "\n")

            g.spectroData = []
            for i in range(min(len(counts), len(energy))):
                csvfile.write(f"{energy[i]:9.4f}, {counts[i]}\n")
                g.spectroData.append([energy[i], counts[i]])                     # make g.spectroData list

        g.spectroData = np.array(g.spectroData)                                  # convert to numpy array

        return g.spectroData


    ####### end local def ########################################################################################

    defname = "getFileSpectro: "

    if g.debug:
        print(1)
        print(2)
        print(3)
        print(4)
    dprint(defname, f"defaultSpectroDBPath={defaultSpectroDBPath}, source={source}, restart={restart}")
    setIndent(1)

    fname                       = None
    g.spectroDBPath             = None
    g.spectroCurrentFileType    = None
    g.spectroScale              = [0.0, 1.0, 0.0, 0.0]

    # DEFAULT spectro file is given as parameter; so use it; this implies source="Database"
    if defaultSpectroDBPath is not None:
        g.spectroDBPath = defaultSpectroDBPath

    # else - no default file given as parameter, run dialog to get one
    else:
        # in all cases: there must be an existing, readable file; this file will remain unchanged
        if   source == "Database":  # extension is .spectro; do NOT allow to load other files
            dlg=QFileDialog(caption= "Get Spectro - Select from Existing GeigerLog *.spectro File", options=QFileDialog.Option.DontUseNativeDialog)
            dlg.setFileMode(QFileDialog.FileMode.ExistingFile)
            dlg.setNameFilter("Spectro Files (*.spectro)")

        elif source == "CSV-GEN":
            dlg=QFileDialog(caption = "Get Spectro - Select from Existing Generic CSV File", options=QFileDialog.Option.DontUseNativeDialog)
            dlg.setFileMode(QFileDialog.FileMode.ExistingFile)
            dlg.setNameFilter("Spectro Files (*.csv);;Canberra Files (*.tka);;Any Files (*)")

        elif source == "CSV-SPE":  # extension is .csv, .txt, ...
            dlg=QFileDialog(caption = "Get Spectro - Select from Existing CSV File", options=QFileDialog.Option.DontUseNativeDialog)
            dlg.setFileMode(QFileDialog.FileMode.ExistingFile)
            dlg.setNameFilter("Spectro Files (*.csv);;Any Files (*)")

        elif source == "CSV-MC":  # extension is .csv, .txt, ...
            dlg=QFileDialog(caption = "Get Spectro - Select from Existing MC CSV File", options=QFileDialog.Option.DontUseNativeDialog)
            dlg.setFileMode(QFileDialog.FileMode.ExistingFile)
            dlg.setNameFilter("Spectro Files (*.csv);;Any Files (*)")

        elif source == "HDS101-CSV-SPE":  # extension is .spe
            dlg=QFileDialog(caption = "Get Spectro - Select from Existing HDS101 CSV File", options=QFileDialog.Option.DontUseNativeDialog)
            dlg.setFileMode(QFileDialog.FileMode.ExistingFile)
            dlg.setNameFilter("Spectro Files (*.spe)")

        elif source == "XML-RadiaCode":  # extension is .xml
            dlg=QFileDialog(caption = "Get Spectro - Select from Existing RadiaCode XML File", options=QFileDialog.Option.DontUseNativeDialog)
            dlg.setFileMode(QFileDialog.FileMode.ExistingFile)
            dlg.setNameFilter("Spectro Files (*.xml);;Any Files (*)")

        elif source == "XML-N42":  # extension is .n42
            dlg=QFileDialog(caption = "Get Spectro - Select from Existing XML-N42 File", options=QFileDialog.Option.DontUseNativeDialog)
            dlg.setFileMode(QFileDialog.FileMode.ExistingFile)
            dlg.setNameFilter("Spectro Files (*.n42);;Any Files (*)")

        elif source == "CANBERRA-CNF":  # extension is .CNF (Canberra Nuclear File)
            dlg=QFileDialog(caption = "Get Spectro - Select from Existing Canberra CNF File", options=QFileDialog.Option.DontUseNativeDialog)
            dlg.setFileMode(QFileDialog.FileMode.ExistingFile)
            dlg.setNameFilter("Spectro Files (*.cnf)")

        elif source == "CANBERRA-TKA":  # extension is .TKA (from Canberra)
            dlg=QFileDialog(caption = "Get Spectro - Select from Existing Canberra TKA File", options=QFileDialog.Option.DontUseNativeDialog)
            dlg.setFileMode(QFileDialog.FileMode.ExistingFile)
            dlg.setNameFilter("Spectro Files (*.tka)")

        else:
            # programming error
            msg = f"Unrecognized source typ '{source}'"
            efprint(msg)
            ydprint(defname, msg)
            sys.exit(97)

        dlg.setViewMode(QFileDialog.ViewMode.Detail)
        dlg.setWindowIcon(g.iconGeigerLog)
        dlg.setDirectory(g.fileDialogDir)
        dlg.setFixedSize(950, 550)

        # Execute dialog
        if dlg.exec() == QDialog.DialogCode.Accepted:   pass    # QDialog.DialogCode.Accepted - aka a file was selected
        else:                                           return  # QDialog Rejected

        g.fileDialogDir = dlg.directory().path()                # now that file selection is done, remember the directory for next call
        # ydprint(defname, "dlg.directory().path():", dlg.directory().path())

        fnames          = dlg.selectedFiles()                   # list of all selected files (but can be only a single one!)
        fname           = fnames[0]                             # file path of first (and only) file
        g.spectroDBPath = fname
        # cdprint(defname, f"Selected file: Sourc {source}  Filenam  {fname}")

    ### a file, containing a spectrum,  is defined - not necessarily a 'spectro' file!

    ### is the file readable?
    if isFileReadable(g.spectroDBPath):
        gdprint(defname, f"Selected Source: {source:15s} File is readable:  '{g.spectroDBPath}'")
    else:
        efprint(f"Selected Source: {source:15s} \nFile '{g.spectroDBPath}'\nis NOT readable. Please, review.")
        return

    ### will the database file (to be created) be writeable?
    if source != "Database":
        newDBspectroFile = g.spectroDBPath + ".spectro"
        if not isFileWriteable(newDBspectroFile):
            msg = f"Required Target: {'spectro':15s}  File '{newDBspectroFile}'\nis not writeable. Please, review."
            efprint(msg)
            rdprint(defname, msg.replace("\n", " "))
            return
        else:
            gdprint(defname, f"Selected Target: {'spectro':15s} File is writeable: '{newDBspectroFile}'")
    else:
        gdprint(defname, "As 'Database' file was requested, writing a 'spectro' File is not needed.")


    ### files for reading / writing are defined and are accessible

    if not quiet: fprint(header("Get Spectro"))

    if source == "Database":
        ### loading ONLY Database files
        ### an existing Spectro file was selected as source file; it has file extension '.spectro'
        if not quiet: fprint(f"Loaded Spectro Database File:\n{g.spectroDBPath}")

        g.spectroData       = getSpectroDataFromSpectroFile(g.spectroDBPath)
        g.spectroDataLen    = len(g.spectroData)
        g.spectroScale      = g.spectroScaleOrig.copy()                   # get the energy calibration parameters

        # Energy and Counts - Original data
        g.EnergyOrig        = g.spectroData[:, 0].copy()
        g.Counts            = g.spectroData[:, 1].copy()

        # Channel Width - from Original data
        g.ChnlWidthOrig     = g.EnergyOrig[1:] - g.EnergyOrig[0:-1]       # last value missing
        g.ChnlWidthOrig     = np.append(g.ChnlWidthOrig, g.NAN)           # add last value to get original length

        # Calib Energy (deried from Energy data fitted with polynome)
        g.EnergyCalib       = PolynomValue(np.array(range(0, g.spectroDataLen)), *g.spectroScale)

        # Channel Width - from Calib Energy   (after fitted with polynome)
        g.ChnlWidthCalib    = g.EnergyCalib[1:] - g.EnergyCalib[0:-1]     # last value missing
        g.ChnlWidthCalib    = np.append(g.ChnlWidthCalib, g.NAN)          # add last value to get full length

        ### predefining 'np.full' arrays: "Return a new array of given shape and type, filled with fill_value(=g.NAN)."
        g.clipEnergy        = np.full(g.spectroDataLen, g.NAN)    # energy data - after clipping
        g.clipCounts        = np.full(g.spectroDataLen, g.NAN)    # count  data - after clipping

        g.clipFitEnergy     = np.full(g.spectroDataLen, g.NAN)    # energy data - as used for fit
        g.clipFitCounts     = np.full(g.spectroDataLen, g.NAN)    # count  data - as used for fit

        g.fitResult         = np.full(g.spectroDataLen, g.NAN)    # count  data - as result of fitted Gauss functions
        g.fitQuality        = np.full(g.spectroDataLen, g.NAN)    # qual   data - as result of fitted Gauss functions

        # printArrays(defname)  # if needed

    else:
        ### all except Database files (converting foreign standards to GeigerLog spectro)

        getfileStart = time.time()

        g.spectroCurrentFileType = source
        fname = g.spectroDBPath
        if   source == "CSV-GEN":                 saveSpectroCSVFile            (fname, fname + ".spectro") # CSV
        elif source == "CSV-SPE":                 saveSpectroCSVFile            (fname, fname + ".spectro") # -"-
        elif source == "CSV-MC":                  saveSpectroCSVFile            (fname, fname + ".spectro") # -"-
        elif source == "HDS101-CSV-SPE":          saveSpectroHDS101CSVFile      (fname, fname + ".spectro") # -"-
        elif source == "CANBERRA-TKA":            saveSpectroCSVFile            (fname, fname + ".spectro") # -"-
        elif source == "CANBERRA-CNF":            saveSpectroCNFFile            (fname, fname + ".spectro") # CNF
        elif source == "XML-RadiaCode":           saveSpectroXML_RadiaCodeFile  (fname, fname + ".spectro") # XML
        elif source == "XML-N42":                 saveSpectroXML_N42File        (fname, fname + ".spectro") # XML
        else:
            esprint(f"Unrecognized File Type of sourc '{source}'")
            burp()
            sys.exit(99)

        if not quiet:
            fprint(f"Created Spectro Database for '{source}' from Source File:\n{fname}")

        g.spectroDBPath += ".spectro"
        cdprint(defname, f"re-calling: fname: {fname}  g.spectroDBPath: {g.spectroDBPath}")
        if not quiet:
            fprint(f"Loading Spectro Database File:\n{g.spectroDBPath}")

        getFileSpectro(defaultSpectroDBPath=g.spectroDBPath, source="Database", restart=False)

        # printArrays(defname)  # if needed

        if getfileStart is not None:
            getfileStop = time.time()
            getfileDur   = getfileStop - getfileStart
            mdprint(defname, f"Dur getting DB: {getfileDur:0.3f} sec")
        else:
            irdprint(defname, f"getfileStart is None")

    # allow adding Spectro comments once a Spectro file is defined
    if g.spectroDBPath is not None: g.exgg.addSpectroCommentAction.  setEnabled(True)
    else:                           g.exgg.addSpectroCommentAction.  setEnabled(False)

    setIndent(0)

    if restart: initSpectroGraph(reset=True)


def appendComments(comments):               # PLURAL!

    defname = "appendComments: "

    with (open(g.spectroDBPath, "a")) as spectrofile:               # comment as top entry
        for comment in comments:
            comment = comment.strip()
            g.spectroCommentsOrg += [comment]
            dprint(f"{defname}'{comment}'")

            if not comment.endswith("\n"):  comment += "\n"
            if not comment.startswith("#"): comment  = "#G " + comment

            spectrofile.write(comment)

    # must reload to see appended comment
    getFileSpectro(defaultSpectroDBPath=g.spectroDBPath, source="Database", restart=False)


def saveSpectroGraph():
    """save the main graph to a (png) file"""

    defname = "saveSpectroGraph: "

    sprint(headerSpec("Save Spectro Graph"))

    if g.spectroData is None or len(g.spectroData) <= 1:
        sprint(f"Cannot save - No Data\n")
    else:
        pngpath = g.spectroDBPath + ".png"
        plt.savefig(pngpath)
        sprint(f"Database: {g.spectroDBPath}")
        sprint(f"to file:  {pngpath}\n")


#test
def makeSimulDataFiles():
    """Test Data consisting of multiple Gausss curves"""

    #### Begin Local defs ####################################################
    def appendBump(fileName, index):
        """adds count spikes to the final channels"""

        return

        with (open(fileName, "a") as csvtest):
            for i in range(index, index + 4):
                energy = getEnergyFromChannel(i, coefficients)
                gsum   = 0
                for specsi in specs:  gsum += 5
                line = f"{energy:0.2f}, {gsum:0.2f}"
                # print(f"i: {i}  lin {line}")
                csvtest.write(line + "\n")

            for i in range(index + 4, index + 40):
                energy = getEnergyFromChannel(i, coefficients)
                gsum   = 0
                for specsi in specs:  gsum += 0
                line = f"{energy:0.2f}, {gsum:0.2f}"
                # print(f"i: {i}  lin {line}")
                csvtest.write(line + "\n")

            for i in range(index + 40, index + 48):
                energy = getEnergyFromChannel(i, coefficients)
                gsum   = 0
                for specsi in specs:  gsum += 20
                line = f"{energy:0.2f}, {gsum:0.2f}"
                # print(f"i: {i}  lin {line}")
                csvtest.write(line + "\n")


    def getEnergyFromChannel(channel, coefficients):
        """Calculates the Energy for a given channel based on Coefficients"""

        a, b, c, d = coefficients

        return a + b * channel + c * channel**2 + d * channel**3

    #### End Local defs ######################################################


    defname     = "makeSimulDataFiles: "
    spectroPeak = 100
    spectroList = [511,             # Na-22 und 511 keV annihilation
                   661.7,           # Cs-137
                   1173.2,          # Co-60
                   1332.501,        # Co-60
                #    1460.81 - 217,   # K-40 Compton edge = 1243
                   1460.81,         # K-40
                   2614.533,        # Tl-208
                   3333.33,         # fantasy
                   ]

    dprint(defname)
    setIndent(1)

    # This uses Fixed RELATIVE FWHM = 0.589%
    specs        = []
    coefficients = [0.0, 2.0, 0.0, 0.0]

    for spectroMean in spectroList:
        FWHM         = 0.0589 * spectroMean
        spectroSigma = FWHM / 2.3548
        specs.append((spectroPeak, spectroMean, spectroSigma))

    dprint(defname, "Test data spectroTestFWHMRelative")

    fileName    = "data/Simul_FWHM=5.89%.spectro"
    with (open(fileName, "w") as csvtest):
        csvtest.write(f"#G {'File Type':22s}: CSV-GEN\n")
        csvtest.write(f"# Test Data Simulation, using multiple Gauss functions\n")
        csvtest.write(f"# with relative FWHM constant = 5.89% for all energies\n")
        csvtest.write(f"# {'Manufacturer':20s}: GeigerLog\n")
        csvtest.write(f"# {'Detector Type':20s}: CsI - Simulation\n")
        csvtest.write(f"# {'Device':20s}: Python\n")
        csvtest.write(f"# {'Orig. Calib. Coeffs':20s}: {coefficients}\n")

        for i in range(2000):
            energy = getEnergyFromChannel(i, coefficients)
            gsum   = 0
            for specsi in specs:  gsum += np.round(Gauss(energy, *specsi), 0)
            line   = f"{energy:0.2f}, {gsum:0.2f}"
            # print(f"i: {i}  lin {line}")
            csvtest.write(line + "\n")

    appendBump(fileName, 2000)

    ### This uses Fixed ABSOLUTE FWHM = 85 keV
    specs        = []
    coefficients = [0.0, 2.0, 0.0, 0.0]

    for spectroMean in spectroList:
        FWHM         = 85
        spectroSigma = FWHM / 2.3548
        specs.append((spectroPeak, spectroMean, spectroSigma))

    dprint(defname, "Test data spectroTestFWHMAbsolute")

    fileName    = "data/Simul_FWHM=85keV.spectro"
    with (open(fileName, "w") as csvtest):
        csvtest.write(f"#G {'File Type':22s}: CSV-GEN\n")
        csvtest.write(f"# Test Data Simulation, using multiple Gauss functions\n")
        csvtest.write(f"# with FWHM constant = 85 keV for all energies\n")
        csvtest.write(f"# {'Manufacturer':20s}: GeigerLog\n")
        csvtest.write(f"# {'Detector Type':20s}: CsI - Simulation\n")
        csvtest.write(f"# {'Device':20s}: Python\n")
        csvtest.write(f"# {'Orig. Calib. Coeffs':20s}: {coefficients}\n")

        for i in range(2000):
            energy = getEnergyFromChannel(i, coefficients)
            gsum   = 0
            for specsi in specs:  gsum += np.round(Gauss(energy, *specsi), 0)
            line   = f"{energy:0.2f}, {gsum:0.2f}"
            # print(f"i: {i}  lin {line}")
            csvtest.write(line + "\n")

    appendBump(fileName, 2000)

    ### This uses Fixed Absolute FWHM = 1 keV
    specs        = []
    coefficients = [0.0, 0.5, 0.0, 0.0]             # 0.5 keV / channel

    for spectroMean in spectroList:
        FWHM         = 1
        spectroSigma = FWHM / 2.3548
        specs.append((spectroPeak, spectroMean, spectroSigma))

    dprint(defname, "Test data spectroTestFWHMAbsolute")

    fileName    = "data/Simul_FWHM=1keV.spectro"
    with (open(fileName, "w") as csvtest):
        csvtest.write(f"#G {'File Type':22s}: CSV-GEN\n")
        csvtest.write(f"# Test Data Simulation, using multiple Gauss functions with\n")
        csvtest.write(f"# FWHM constant = {FWHM} keV for all energies and keV/Chnl = {coefficients[1]}\n")
        csvtest.write(f"# {'Manufacturer':20s}: GeigerLog\n")
        csvtest.write(f"# {'Detector Type':20s}: BEGe - Simulation\n")
        csvtest.write(f"# {'Device':20s}: Python\n")
        csvtest.write(f"# {'Orig. Calib. Coeffs':20s}: {coefficients}\n")

        for i in range(8000):
            energy = getEnergyFromChannel(i, coefficients)
            gsum   = 0
            for specsi in specs:  gsum += np.round(Gauss(energy, *specsi), 0)
            line   = f"{energy:0.2f}, {gsum:0.2f}"
            # print(f"i: {i}  lin {line}")
            csvtest.write(line + "\n")

    appendBump(fileName, 8000)


    ### This uses only Cs-137 with FWHM of radiacode 102:  9.4% ±0.4% (FWHM) for Cs-137, 103: 8.4% ±0.3% (FWHM) for Cs-137
    specs        = []
    coefficients = [0.0, 2.0, 0.0, 0.0]             # 0.5 keV / channel

    spectroPeak = 100
    spectroList = [ 500.0,          # positioned at 1000 keV with FWHM = 9.4%
                   1000.0,          # positioned at 1000 keV with FWHM = 8.4%
                   1500.0,          # positioned at 1000 keV with FWHM = 7.4%
                   ]

    for i, spectroMean in enumerate(spectroList):
        if   i == 0:         FWHM         = 0.094 * 661.7
        elif i == 1:         FWHM         = 0.084 * 661.7
        elif i == 2:         FWHM         = 0.074 * 661.7
        spectroSigma = FWHM / 2.3548
        specs.append((spectroPeak, spectroMean, spectroSigma))

    dprint(defname, "SimulData_Cs137@Radiacode 102, 103 FWHM")

    fileName    = "data/Simul_Cs137@Radiacode_FWHMs.spectro"
    with (open(fileName, "w") as csvtest):
        csvtest.write(f"#G {'File Type':22s}: CSV-GEN\n")
        csvtest.write(f"# Test Data Simulation, using Gauss functions with\n")
        csvtest.write(f"# FWHM = {FWHM} keV and keV/Chnl = {coefficients[1]}\n")
        csvtest.write(f"# {'Manufacturer':20s}: GeigerLog\n")
        csvtest.write(f"# {'Detector Type':20s}: RadiaCode - Simulation\n")
        csvtest.write(f"# {'Device':20s}: Python\n")
        csvtest.write(f"# {'Orig. Calib. Coeffs':20s}: {coefficients}\n")

        for i in range(1024):
            energy = getEnergyFromChannel(i, coefficients)
            gsum   = 0
            for specsi in specs:  gsum += np.round(Gauss(energy, *specsi), 0)
            line   = f"{energy:0.2f}, {gsum:0.2f}"
            # print(f"i: {i}  lin {line}")
            csvtest.write(line + "\n")


    dprint(defname, "Finished")
    setIndent(0)


def getSpectroInfo():
    """give an overview on the original data as Info"""
    # original data like: [4.16120e+03 0.00000e+00] [4.16466e+03 0.00000e+00] [4.16812e+03 0.00000e+00] ...

    defname = "getSpectroInfo: "
    msg     = ""

    if g.spectroData is None or g.spectroDBPath is None:
        msg += "No Data"

    else:
        channels = len(g.spectroData)
        try:     MaxE, MaxC = g.spectroData.max(axis=0)         # max energy, max counts
        except:  MaxE, MaxC = g.NAN, g.NAN

        try:     MinE, minC = g.spectroData.min(axis=0)         # min energy, min counts
        except:  MinE, minC = g.NAN, g.NAN
        cdprint(defname, f"MinE: {MinE}  MaxE: {MaxE}  minC: {minC}  MaxC: {MaxC}  ")

        CalibMinE = g.EnergyCalib[0]
        CalibMaxE = g.EnergyCalib[-1]

        msg += f"Spectrum:\n"
        msg += f"  {'Database'              :21s} : {g.spectroDBPath.replace(os.getcwd(), '.')}\n"

        # irdprint(defname, f"g.spectroCommentsGlg: {g.spectroCommentsGlg}")
        for ccs in g.spectroCommentsGlg:
            if "Calibration" not in ccs:
                ccs  = (ccs.strip())[3:]
                sccs = ccs.split("::", 1)
                if len(sccs) == 2:  msg += f"  {sccs[0].strip():21s} : {sccs[1].strip()}\n"
                else:               msg += f"  {ccs}\n"

        msg += f"  {'Channels'              :21s} : {channels}\n"
        msg += f"  {'Counts'                :21s} : Min: {minC:<7,.6g}  Max: {MaxC:<7,.6g}    Total: {g.spectroData.sum(axis=0)[1]:<0,.8g}\n"

        for ccs in g.spectroCommentsGlg:
            if "Calibration" in ccs:
                ccs  = (ccs.strip())[3:]
                sccs = ccs.split("::", 1)
                if len(sccs) == 2:  msg += f"  {sccs[0].strip():21s} : {sccs[1].strip()}\n"
                else:               msg += f"  {ccs}\n"

        msg += f"\n"
        msg += f"META Data from Original File:\n"
        for cc in g.spectroCommentsOrg:
            ccs  = str((cc.strip())[2:])
            sccs = ccs.split("::", 1)
            if len(sccs) == 2:  msg += f"  {sccs[0].strip():21s} : {sccs[1].strip()}\n"
            else:               msg += f"  {ccs}\n"

        msg  += "\n"
        msg += f"{'Calibration:'}\n"
        msg += f"{'  Active Calibration'  :22s}  : [{', '.join(f'{ss:0.9g}' for ss in g.spectroScale)}]\n"
        msg += f"{'  Energy-Range [keV]'  :22s}  : Min: {CalibMinE:<7,.3f}  Max: {CalibMaxE:<7,.3f}\n"

        # get First and last 10 original recs
        if 1:
            msg += "\n"
            msg += "  First and Last 10 Records  (#index :: Energy [keV]:Counts):\n"
            xarray, yarray = g.EnergyCalib, g.Counts

            start = 0
            end   = start + 10
            msg  += f"    #{start:<4d} :: "
            for i in range(start, end):
                msg += f"{xarray[i]:9.3f}:{yarray[i]:<5.2f} "
            msg  += "\n"

            start = len(xarray) - 10
            end   = start + 10
            msg  += f"    #{start:<4d} :: "
            for i in range(start, end):
                msg += f"{xarray[i]:9.3f}:{yarray[i]:<5.2f} "
            msg  += "\n"

    return msg


def getSpectroData(selection="CUMULATE"):
    """get the full original data as list"""
    # original data like: [4.16120e+03 0.00000e+00] [4.16466e+03 0.00000e+00] [4.16812e+03 0.00000e+00] ...

    defname = "getSpectroData: "
    msg     = ""

    if g.spectroData is None:
        msg += f"{'No Data':25s}\n"
    else:
        if selection == "CUMULATE": xarray, yarray = g.clipEnergy,          g.clipCounts
        else:                       xarray, yarray = g.spectroData[:, 0],   g.spectroData[:, 1]
        lenarray = len(xarray)
        cdprint(defname, f"lenarray {selection}: ", lenarray)

        if g.spectroData is None:
            msg += f"{'No Data':25s}\n"
        else:
            cols = 10

            # header
            msg += f"#Index  [Channel | Energy[keV] : Counts]  ...\n"

            # ruler for top and bottom
            rul  = f"#####     "
            for i in range(cols): rul += f"{i:1d}{'-' * 8}------ "
            msg += rul +"\n"

            for i in range(lenarray):
                if i % cols == 0:       sdstep = f"#{i:<4d}     "
                sdstep += f"{xarray[i]:7.2f} : {yarray[i]:<4.0f}  "
                if (i + 1) % cols == 0: msg += sdstep + "\n"
            if (i + 1) % cols != 0: msg += sdstep + "\n"                    # need final "\n" to set Cursor on left at the end
            msg += rul + "\n"

            msg += f"{'Database File' :22s}: {g.spectroDBPath.replace(os.getcwd(), '.')}\n"
            msg += f"{'Clipped Recs'  :22s}: {lenarray        :<4d}    original: {len(g.spectroData[:, 0])}\n"
            msg += f"{'Clipped Counts':22s}: {np.sum(yarray):<7.0f} original: {np.sum(g.spectroData[:, 1]):0.0f}\n"

    return msg


def getSpectroGraphDataAll():
    """get the data as currently shown in the graph"""

    ######################################################################################
    def makePrntout(Spectrum):
        """Print to NotePad all checked Spectra and Properties"""

        global msg

        lenarray = len(xarray)
        cdprint(defname, f"lenarray: ", lenarray)

        msg += f"{'Data Type'   :17s}: {Spectrum}\n"
        msg += f"{'Data Records':17s}: {lenarray}\n"
        msg += msg2

        # header
        msg += rulerheader

        # ruler for top and bottom
        cols = 10
        rul  = f"#####     "
        for i in range(cols): rul += f"{i:1d}{'-' * 15}  "
        msg += rul +"\n"

        for i in range(lenarray):
            if i % cols == 0:       sdstep = f"#{i:<4d}     "
            # sdstep += f"{xarray[i]:7.2f} :{customformat(yarray[i], 7, 2, thousand=False):>7s}  "   # total, dec, thousand=True):
            # sdstep += f"{xarray[i]:7.2f}:{customformat(yarray[i], 7, 2, thousand=False):>7s}  "   # total, dec, thousand=True):
            sdstep += f"{xarray[i]:8.3f}:{customformat(yarray[i], 7, 2, thousand=False):>7s}  "   # total, dec, thousand=True):
            if (i + 1) % cols == 0: msg += sdstep + "\n"

        if (i + 1) % cols != 0: msg += sdstep + "\n"                    # need final "\n" to set Cursor on left at the end
        msg += rul +"\n"
        msg += "\n"

    ######################################################################################

    global msg

    defname             = "getSpectroGraphDataAll: "
    msg                 = ""
    msg2                = ""
    rulerheader         = ""
    xarray, yarray      = [], []

    if g.spectroData is None:
        msg += f"{'No Data':25s}\n"
        return msg

    msg += f"{'Database File'    :17s}: {g.spectroDBPath.replace(os.getcwd(), '.')}\n"
    msg += f"{'Original Records' :17s}: {len(g.spectroData[:, 0])}\n"
    msg += f"{'Original Counts'  :17s}: {np.sum(g.spectroData[:, 1]):0.0f}\n"
    msg += "---------\n"

    if g.spectroShowSpec:
                                # xarray, yarray = g.clipEnergy, g.clipCounts
                                xarray, yarray = g.EnergyCalib, g.clipCounts
                                msg2         = f"{'Data Counts':17s}: {np.sum(yarray):<7.0f}\n"
                                rulerheader  = f"#Index  [Energy [keV]: Counts] ...\n"
                                makePrntout("Spectrum Calibrated")

    if g.spectroShowFit:
                                xarray, yarray = g.clipFitEnergy, g.fitResult
                                msg2         = f"{'Data Counts':17s}: {np.sum(yarray):<7.0f}\n"
                                rulerheader  = f"#Index  [Energy [keV]: Counts] ...\n"
                                makePrntout("Spectrum Fit")

    if g.spectroShowSearchPeak:
                                # xarray, yarray = g.clipEnergy, g.clipfitQuality
                                xarray, yarray = g.EnergyCalib, g.clipfitQuality
                                msg2         = f"{'Data Values':17s}: {np.nansum(yarray):<7.0f}\n"
                                rulerheader  = f"#Index  [Energy [keV] : Value] ...\n"
                                makePrntout("Spectrum Peaks")

    if g.spectroShowChnlW:
                                # xarray, yarray = g.clipEnergy, g.ChnlWidthOrig
                                xarray, yarray = g.EnergyCalib, g.ChnlWidthOrig
                                msg2         = f"{'Data Counts':17s}: N.A.\n"
                                rulerheader  = f"#Index  [Gamma Energy [keV] : Channel Width [keV]] ...\n"
                                makePrntout("Spectrum Width vs Energy")

    if g.spectroShowOrig:
                                channels        = range(0, g.spectroDataLen)
                                xarray, yarray  = g.Counts, channels
                                msg2            = f"{'Data Counts':17s}: {np.sum(xarray):<7.0f}\n"
                                msg2           += "Not Original data - Energy data may be Channel Number!\n"
                                rulerheader     = f"#Index  [Counts : Channel No] ...\n"
                                makePrntout("Spectrum Original")

    return msg


def showSpectroInfo(original=False):
    """print to MAIN NotePad and Terminal  all info"""

    defname = "showSpectroInfo: "

    fprint(header("Show Spectro Info"))

    if g.spectroData is None:
        msg = "No Data"
        efprint(msg)

    else:
        if not original:
            getinfo = getSpectroInfo()
            fprint(getinfo)

        else:
            fprint("Original data:")
            if   g.spectroCurrentFileType == "CSV-GEN":         showSpectroCSVInfo()    # CSV
            elif g.spectroCurrentFileType == "CSV-SPE":         showSpectroCSVInfo()    # -"-
            elif g.spectroCurrentFileType == "CSV-MC":          showSpectroCSVInfo()    # -"-
            elif g.spectroCurrentFileType == "CANBERRA-TKA":    showSpectroCSVInfo()    # -"-
            elif g.spectroCurrentFileType == "CANBERRA-CNF":    showSpectroCNFInfo()    # CNF
            elif g.spectroCurrentFileType == "XML-N42":         showSpectroXMLInfo()    # XML
            elif g.spectroCurrentFileType == "HDS101-SPE":      showSpectroCSVInfo()    # CSV   ??????????????????
            elif g.spectroCurrentFileType == "XML-RadiaCode":   showSpectroXMLInfo()    #
            else:                                               showSpectroCSVInfo()


def showSpectroCSVInfo():
    """print original CSV file"""

    defname = "showSpectroCSVInfo: "

    filepath = os.path.splitext(g.spectroDBPath)[0]      # file basename with path w/o ext; should remove ext=spectro
    if os.path.isfile(filepath):
        with open(filepath, "r" ) as csvfile: alldata = csvfile.readlines()
        # cdprint(defname, f"alldata:  typ{type(alldata)}  len:{len(alldata)} alldata: {alldata[:6]}")
        for line in alldata: fprint(line)
        fprint("")
    else:
        fprint(f"An original data file cannot be found: {filepath}")


def showSpectroCNFInfo():
    """print CNF dictionary"""

    fprint("NOTE: Original data are non-printable binary; printing instead extracted data:")
    cnfpath    = os.path.splitext(g.spectroDBPath)[0]                          # file basename with path w/o ext
    cnfcontent = gsup_spectro_cnf.read_cnf_file(cnfpath, write_output=False)   # use "write_output=True" in order to get a file with ext=text with Dict data
    for cc in cnfcontent:
        fprint(f"{cc:20s}: {cnfcontent[cc]}")


def showSpectroXMLInfo():
    """PrettyPrint XML file content to Main NotePad and Terminal"""

    defname = "showSpectroXMLInfo: "

    xmlpath = os.path.splitext(g.spectroDBPath)[0]      # file basename with path w/o ext
    with open(xmlpath, "r" ) as xmlfile:
        alldata = xmlfile.readlines()

    stralldata = "".join(dd for dd in alldata)          # brauche string für Parser
    # cdprint(defname, f"stralldata:  typ{type(stralldata)}  len:{len(stralldata)} stralldata: {stralldata[:120]}")

    ### parse the xml data string
    try:
        parser = etree.XMLParser(ns_clean=True, recover=True)           # recover allows to ignore missing DHS definition
        root   = etree.fromstring(stralldata, parser)
    except etree.ParseError as e:
        exceptPrint(e, "ParseError parsing XML file")
        efprint("Failure loading XML file!")
    except Exception as e:
        exceptPrint(e, "Non-ParseError Exception parsing XML file")
        efprint("Failure loading XML file!")
    else:
        xml = etree.tostring(root, pretty_print=True)
        fprint(cleanHTML(xml.decode()))


def showSpectroData():
    """print to MAIN NotePad and Terminal  all original channel/energy & Counts data """

    defname = "showSpectroData: "

    fprint(header("Show Spectro Data"))

    if g.spectroData is None:
        msg = "No Data"
        efprint(msg)
        cdprint(defname, msg)
    else:
        getdata = getSpectroData(selection="FULL")
        fprint(getdata)
        cdprint(defname, "\n", getdata)


def calibChannelToEnergy(channel):
    """Apply 3rd order polynom for calibration of channel to energy"""

    a, b, c, d = g.spectroScale
    cal = a + b * channel + c * channel**2 + d * channel**3

    return cal


def getComptonEdge(gammaenergy):
    """gets the Compton Edge for gamma particle of gammaenergy in keV"""
    # Compton-Edge (CE): CE = Egamma * ( 1 -  1 / (1 + 2 * Egamma / mc²))
    # using: Egamma for K40 = 1460.81 keV  with m of electron = 511 keV / c²
    # CE = 1460 * ( 1 -  1 / (1 + 2 * 1460 / 511) ) = 1243.35 keV  (Delta Egamma - C 217.46 keV)

    defname = "getComptonEdg "

    ### se Introduction of https://www.sciencedirect.com/science/article/abs/pii/S0168900215007512
    cedge = gammaenergy * (2 * gammaenergy / (511 + 2 * gammaenergy))

    return cedge


def onSpectroPress(event):
    """gets keypresses"""

    if event.inaxes:
        cdprint(f"you pressed: key: {event.key} x: {event.xdata} y: {event.ydata}")


def onSpectroMove(event):
    """gets the mouse movements (- works!)"""

    if event.inaxes:
        # print(f'data coords {event.xdata} {event.ydata}   pixel coords {event.x} {event.y}')
        if event.button is not None: cdprint(event)


#on
def onSpectroClick(event):
    """on mouseclick in spectro graph enter time coords into xmin, xmax; left click = xmin, right click = xmax"""
    # IMORTANT: Canvas MUST have focus to recognize keypresses !!!

    #################################################################################
    def getYLeft(y):

        yLbottom, yLtop = sax1.get_ylim()
        yRbottom, yRtop = sax2.get_ylim()

        yR = y / (yRtop - yRbottom)
        yL = (yLtop - yLbottom) * yR + yLbottom

        return yL
    #################################################################################

    defname = "onSpectroClick: "

    try: # if no data are shown, this may result in non-breaking error messages
        if event.inaxes:
            x   = event.xdata
            yR  = event.ydata
            b   = event.button
            c   = event.buttons   # geht nicht
            d   = event.dblclick
            key = event.key

            button = ("Left  ", "Middle", "Right ")[b - 1]
            if not g.canvasSpectro.hasFocus():
                cocoo()
                sprint(defname + "CANVAS HAS NO FOCUS")
                g.canvasSpectro.setFocus()
            gdprint(defname, f"inaxes:  x:{x:8.3f}  yR:{yR:8.3f} -> yL:{getYLeft(yR):8.3f}  b:{button}  c:{c}  dbl:{d}  key:{str(key):8s} hasFocus:{g.canvasSpectro.hasFocus()} ")

            # clip
            if key in ("control",):
                # left Clip
                if "Left" in button:
                    g.spectroLeftClipEnergy = x
                    g.spectroLeftClipCounts = 0
                    g.spectroLeftClipBox .setText(f"{x}")      # left  click, xLeft
                    if float(g.spectroLeftFitBox .text().strip().replace(",", "")) < x:
                        g.spectroLeftFitEnergy = x
                        g.spectroLeftFitBox.setText(f"{x}")

                # right Clip
                elif "Right" in button:
                    g.spectroRightClipEnergy = x
                    g.spectroRightClipCounts = 0
                    g.spectroRightClipBox.setText(f"{x}")      # right click, xRight
                    if float(g.spectroRightFitBox .text().strip().replace(",", "")) > x:
                        g.spectroRightFitEnergy = x
                        g.spectroRightFitBox.setText(f"{x}")

                clipSpectrumData()
                makeFitPeak()
                clipSpectrumData()
                updateEditBoxes()
                plotGraphSpectro()

            # fit
            else:
                # middle click
                if "Middle" in button:
                    # irdprint(defname, "Middle Click")
                    g.spectroLeftFitCounts      = 0
                    g.spectroRightFitCounts     = 0
                    g.spectroBackground         = None
                    g.spectroBackgroundLimits   = [0, 0]
                    getPeakFitMiddleClick(x)

                # left, right click
                else:
                    # irdprint(defname, "Left or Right Click")
                    try:    currentLeftFit  = float(g.spectroLeftFitBox .text().strip().replace(",", "."))
                    except: currentLeftFit  = g.NAN
                    try:    currentRightFit = float(g.spectroRightFitBox.text().strip().replace(",", "."))
                    except: currentRightFit = g.NAN
                    g.spectroBackgroundLimits   = [0, 0]

                # left click
                    if   b == 1:
                        if x >= g.spectroLeftClipEnergy:     g.spectroLeftFitEnergy = x
                        else:                                g.spectroLeftFitEnergy = g.spectroLeftClipEnergy
                        y = getYLeft(yR)
                        y = 10**y if g.spectroShowLog else y
                        g.spectroLeftFitCounts = max(0, y)
                        g.spectroLeftFitBox .setText(f"{x:0.2f}")
                        if currentRightFit < x:
                            g.spectroRightFitBox.setText(f"{x *1.0:0.2f}")
                            g.spectroRightFitEnergy = x * 1.0

                    # right click
                    elif b == 3:
                        if x <= g.spectroRightClipEnergy:    g.spectroRightFitEnergy = x
                        else:                                g.spectroRightFitEnergy = g.spectroRightClipEnergy
                        y = getYLeft(yR)
                        y = 10**y if g.spectroShowLog else y
                        g.spectroRightFitCounts = max(0, y)
                        g.spectroRightFitBox.setText(f"{x:0.2f}")
                        if currentLeftFit  > x:
                            g.spectroLeftFitBox .setText(f"{x /1.0:0.2f}")
                            g.spectroLeftFitEnergy = x / 1.0

                    msg   = f"xL:{g.spectroLeftFitEnergy:7.3f} xR:{g.spectroRightFitEnergy:7.3f} | yL:{g.spectroLeftFitCounts:7.3f} yR:{g.spectroRightFitCounts:7.3f}"
                    cdprint(defname, msg)

                    getPeakFitROI(print=False)

    except Exception as e:
        exceptPrint(e, defname)


#fit
def makeFitPeak(type="ROI"):
    """Fits a Gauss curve to the ROI (Region of interest)"""
    # type="Middle"   # estimates borders itself
    # type="ROI"      # takes borders as clicked by user

    defname = "makeFitPeak: "
    # irdprint(defname)

    # if not g.spectroShowFit: return False

    # clip the fit data
    listclipFitEnergy = []
    listclipFitCounts = []
    for i in range(0, g.spectroDataLen - g.spectroCumul + 1, g.spectroCumul):
        if g.EnergyCalib[i] >= g.spectroLeftFitEnergy and g.EnergyCalib[i] <= g.spectroRightFitEnergy:
            fitenrg, fitcnts = 0, 0
            for j in range(g.spectroCumul):
                fitenrg += g.EnergyCalib[i + j]
                fitcnts += g.Counts[i + j]

            listclipFitEnergy  .append(fitenrg / g.spectroCumul)
            listclipFitCounts  .append(fitcnts)

    g.clipFitEnergy = np.array(listclipFitEnergy)
    g.clipFitCounts = np.array(listclipFitCounts)
    g.fitResult     = g.clipFitCounts.copy()

    if not g.spectroShowFit:
        # irdprint(defname, f"g.spectroShowFit: {g.spectroShowFit}")
        # irdprint(defname, f"g.fitResult:   len: {len(g.fitResult)}   {g.fitResult[0:3]}  sum: {np.sum(g.fitResult)}")
        g.fitResult     = np.full(len(g.fitResult), g.NAN)
        # irdprint(defname, f"g.fitResult:   len: {len(g.fitResult)}   {g.fitResult[0:3]}  sum: {np.sum(g.fitResult)}")
        return False

    if len(g.clipFitEnergy) == 0:
        sprint(headerSpec("Fit Peak"))
        msg = "No data left in clipped range. Cannot make Fit."
        sprint(msg)
        sprint("")
        rdprint(defname, msg)
        g.fitSuccess = False
        return False

    if 0: # to print or not to print
        # mdprint(defname, f"spectroShowFit: ", g.spectroShowFit)
        mdprint(defname, f"clipFitEnergy:  len: {len(g.clipFitEnergy)}  {g.clipFitEnergy[0:10]} ...")
        mdprint(defname, f"clipFitCounts:  len: {len(g.clipFitCounts)}  {g.clipFitCounts[0:10]} ...")

    ### clipped spectrum is available here

    if type == "Middle":
        g.spectroLeftFitCounts  = np.average(g.clipFitCounts[: 5])
        g.spectroRightFitCounts = np.average(g.clipFitCounts[-5: ])

    leftY  = g.spectroLeftFitCounts
    rightY = g.spectroRightFitCounts

    g.spectroBackground         = np.linspace(leftY, rightY, len(g.clipFitCounts))
    g.clipFitCounts            -= g.spectroBackground
    g.spectroBackgroundLimits   = [leftY, rightY]

    if 0:
        # mdprint(defname, f"spectroShowFit: ", g.spectroShowFit)
        mdprint(defname, f"clipFitEnergy:  len: {len(g.clipFitEnergy)}  {g.clipFitEnergy[0:10]} ...")
        mdprint(defname, f"clipFitCounts:  len: {len(g.clipFitCounts)}  {g.clipFitCounts[0:10]} ...")

    ### make the initial guess param0 for the fitting coefficients for a 3 param Gauss fit
    g.spectroPeak         = max(10.0, np.max(g.clipFitCounts))              # param 1
    g.spectroMean         = max(10.0, np.average(g.clipFitEnergy))          # param 2
    g.spectroSigma        = 10.0                                            # param 3

    ### get Fit
    response, g.spectroGaussFitR2 = getGaussFit(g.clipFitEnergy, g.clipFitCounts, g.spectroPeak, g.spectroMean, g.spectroSigma)
    ###
    if response != "Failure":
        # Note: response: (g.fitCoeff, g.fitPCOV, info, msg, flag)
        # for rp in response: print("rp in response: ", rp)
        # cdprint(defname, "info: ", response[2])

        g.fitCoeff      = response[0]
        g.fitPCOV       = response[1]
        # fitinfo       = response[2]   # what to do with it? ignore it
        # fitmsg        = response[3]   # So far was always: "Both actual and predicted relative reductions in the sum of squares are at most 0.000000"
        g.fitFlag       = response[4]

        g.fitSuccess    = True if g.fitFlag in (1, 2, 3, 4) else False
        if g.fitSuccess:
            g.spectroPeak  = g.fitCoeff[0]
            g.spectroMean  = g.fitCoeff[1]
            g.spectroSigma = g.fitCoeff[2]

        # Get the fitted curve
        g.fitResult  = Gauss(g.clipFitEnergy, *g.fitCoeff)
        g.fitResult += g.spectroBackground

    if g.fitSuccess:
        fitcolor = getFitColor(g.spectroGaussFitR2)
        FWHM     = g.spectroSigma * 2.3548
        ELength  = g.clipFitEnergy[-1] - g.clipFitEnergy[0]
        msg = f"Fit: Typ{type:<6s}  Length:Chnl:{len(g.fitResult):<4d}({ELength:<6.2f}keV)  Peak:{g.spectroPeak:<8.2f}  \
                Mean:{g.spectroMean:<9.4f}  Sigma:{g.spectroSigma:<6.2f}  FWHM:{FWHM:<6.2f}  fitFlag:{g.fitFlag}  \
                fitSuccess:{g.fitSuccess}{fitcolor}r2:{g.spectroGaussFitR2:<0.3f}{TDEFAULT}"
        # mdprint(defname, msg)

    return True, g.spectroGaussFitR2


def getPeakFitMiddleClick(x):
    """Fitting after middle click"""

    defname = "getPeakFitMiddleClick: "
    mdprint(defname)
    setIndent(1)

    try:
        g.spectroShowFit = True
        middleEnergy     = x
        FWHM             = 50       # in keV
        loops            = 15
        rsquared         = g.NAN

        for i in range(1, loops + 1):
            # 3 sigma als limit: FWHM = sigma * 2.3548 => sigma = FWHM / 2.3548 => 3 sigma = 1.274* FWHM

            ChnlWidthOrig = getChannelWidth(middleEnergy)
            if FWHM < ChnlWidthOrig * 3: FWHM = 5             # to avoid "no Data" situation

            FWHMmult = 2.0
            xl       = max(middleEnergy - FWHM * FWHMmult, 0)
            xr       = min(middleEnergy + FWHM * FWHMmult, g.EnergyCalib[-1])

            mdprint(defname, f"{i:2d} of {loops}:   Input: E[keV]:{middleEnergy:<7.2f}  EWidth:{xr - xl:<6.2f}  FWHM: {FWHM:6.2f}  r2: {rsquared:0.3f}")

            g.spectroLeftFitEnergy  = xl
            g.spectroRightFitEnergy = xr
            g.spectroLeftFitBox.setText (f"{xl:0.2f}")
            g.spectroRightFitBox.setText(f"{xr:0.2f}")

            ### FIT ###
            success, rsquared = makeFitPeak(type="Middle")
            ###########

            if success:
                middleEnergy = g.spectroMean
                if g.spectroSigma is not None:  FWHM = g.spectroSigma * 2.3548
                else:                           FWHM = g.NAN

            else:
                g.spectroMean  = middleEnergy
                g.spectroSigma = FWHM / 2.3548 * 2

            if i > 3 and rsquared > 0.95 : break
            if np.isnan(middleEnergy):
                middleEnergy = x                # if NAN, reset to original middleEnergy
                FWHM         = 200              # in keV

            ### exiting for loop

        mdprint(defname, "Fit Done")

        clipSpectrumData()
        updateEditBoxes()
        plotGraphSpectro()
        pushPlotToScreen(g.figSpectro)

        if g.fitSuccess:
            if rsquared > 0.8:
                printFitResult()
                bip()
            else:
                burp()
        else:
            burp()

    except Exception as e:
        exceptPrint(e, defname)

    g.checkFit.setChecked(g.spectroShowFit)

    setIndent(0)


def getPeakFitROI(print=True):
    """This is the fit for left-/right-click"""

    defname = "getPeakFitROI"

    try:
        g.spectroShowFit = True
        g.checkFit.setChecked(g.spectroShowFit)

        makeFitPeak(type="ROI")
        clipSpectrumData()
        updateEditBoxes()
        plotGraphSpectro()

        if g.fitSuccess:
            if  g.spectroGaussFitR2 >= 0.8:
                bip()
                printFitResult()
            else:
                burp()
                if print: printFitResult()
        else:
            burp()

    except Exception as e:
        exceptPrint(e, defname)


def Gauss(x, *p):
    """
    Single Gauss function - Model function to be used to fit
    Return: - array of fitted function (or single value if x is single value)
            - on error: x
    """

    defname = "Gauss: "
    # irdprint(defname, f"x:   typ{type(x)}, x:{x[:10]}")                       #: type(x): <class 'numpy.ndarray'>

    Peak, Mean, Sigma = p
    # irdprint(defname, f"Peak:{Peak:<8.2f}, Mean:{Mean:<8.2f}, sigma:{Sigma:<8.2f}")

    try:
        if Sigma != 0:
            GaussVal = Peak * np.exp(-0.5 *((x - Mean) / Sigma)**2)
        else:
            rdprint(defname, "Sigma is zero!")
            GaussVal = x
    except Exception as e:
        exceptPrint(e, defname + f"Gauss Calc  Peak:{Peak:8.2f}, Mean:{Mean:8.2f}, Sigma:{Sigma:8.2f}   x: len:{len(x):8.2f}, typ{type(x)}, x:{x[0:10]}")
        GaussVal = x

    # irdprint(defname, f"GaussVal: len: {len(GaussVal)}  type ReturnVal: {type(GaussVal)}  type ReturnVal[0]: {type(GaussVal[0])} ReturnVals: {GaussVal[:5]} ...")

    return GaussVal


def getGaussFit(energies, counts, peak, mean, sigma):
    """apply a Gauss fit to the given parameters and x and Y value"""

    defname = "getGaussFit: "
    param0  = [peak, mean, sigma]

    ### select Fit Method - options: "lm", "trf", "dogbox"
    g.spectroFitMethod  = "trf"
    # g.spectroFitMethod  = "lm"
    # g.spectroFitMethod  = "dogbox" # blödsinn mit Na-22.cnf

    ### set bounds - possible only for "trf" and "dogbox", NOT for "lm"
    ### ==================================== MIN:[   Peak, Mean, Sigma],    ==== MAX:[   Peak,    Mean,   Sigma]
    if g.spectroFitMethod != "lm":     bounds = ([      1,    2,   0.1],             [+np.inf, +np.inf, +np.inf])   # trf and dogbox
    else:                              bounds = (-np.inf, +np.inf)                                                  # lm
    # irdprint(defname, f"init Fit:  param0: {param0}    method: {method}  bounds: {bounds}")

    try:
        response = "Failure"
        rsquared = g.NAN
        response = scipy.optimize.curve_fit(Gauss, energies, counts, param0, full_output=True, absolute_sigma=True, method=g.spectroFitMethod, bounds=bounds)

    except RuntimeError as e:
        msg = "The maximum number of function evaluations is exceeded"
        if  msg in str(e): rdprint(defname, "FAILURE: " + msg)
        else:              exceptPrint(e, defname + f"Regression failed with Runtime Error")

    except Exception as e:
        exceptPrint(e, defname + "Regression failed with Exception")

    else:
        ### get r_squared
        # residual                         :    residuals = ydata - f(xdata, *popt)
        # sum of residual-squares (ss_res) :    ss_res = numpy.sum(residuals**2)
        # sum of total squares    (ss_tot) :    ss_tot = numpy.sum((ydata - numpy.mean(ydata))**2)
        # r_squared-value :                     r_squared = 1 - (ss_res / ss_tot)
        #
        residuals  = counts - Gauss(energies, *response[0])
        ss_res     = np.sum(residuals**2)
        ss_tot     = np.sum((counts - np.mean(counts))**2)
        if ss_tot != 0:  rsquared = 1 - (ss_res / ss_tot)
        # irdprint(defname, f"ss_res: {ss_res:0.6f},  ss_tot: {ss_tot:0.6f}  r_sqared: {rsquared:0.6f}")
        if rsquared < 0: rsquared = g.NAN

    return response, rsquared


#sp
def findPeaks():
    """Gauss fit all checked isotops"""
    ### NOTES:  from error msg:   SVD is: Singular Value Decomposition

    defname = "findPeaks: "
    dprint(defname)

    g.fitQuality               = np.full(g.spectroDataLen, g.NAN)    # qual data as float - as result of fitted Gauss functions
    getIsotopeData          = g.spectroGammaSelection

    sprint(headerSpec("Finding Peaks"))

    if len(getIsotopeData) == 0:
        msg = "No Isotopes selected. Select one or more Isotopes first."
        dprint(msg)
        esprint(msg)
        sprint()
        return

    setIndent(1)
    mdprint(defname, "getIsotopeData: ", getIsotopeData)
    setBusyCursor()

    sprint(f"{'Isotope':10s} {'E [keV]':>7s} :  {'E-Found':>7s} {'Delta-E':>8s}     FWHM   FWHM% {'Fitr2':>5s} {'Chnls':>5s}")
    g.spectroShowSearchPeak = True

    GammaList = {}

    # Photo Peaks
    PHlist = {}
    for i, iso in enumerate(g.IsotopeData):         # iso is key like K-40
        if iso in getIsotopeData:
            for isoen in g.IsotopeData[iso]:
                PHlist.update({isoen : iso})
    PHsort = dict(sorted(PHlist.items(), reverse=True, key=lambda item: item[0]))
    GammaList.update(PHsort)

    # Compton Edges
    CElist = {}
    for i, iso in enumerate(g.IsotopeData):         # iso is key like K-40
        if iso in getIsotopeData:
            for isoen in g.IsotopeData[iso]:
                if g.plotLineComptonEdge:  CElist.update({getComptonEdge(isoen) : iso + " CE"})
    CEsort = dict(sorted(CElist.items(), reverse=True, key=lambda item: item[0]))
    GammaList.update(CEsort)

    # Single Escape
    SElist = {}
    for i, iso in enumerate(g.IsotopeData):         # iso is key like K-40
        if iso in getIsotopeData:
            for isoen in g.IsotopeData[iso]:
                if isoen < 1022: continue
                if g.plotLineSingleEscape:  SElist.update({isoen - 511  : iso + " SE"})
    SEsort = dict(sorted(SElist.items(), reverse=True, key=lambda item: item[0]))
    GammaList.update(SEsort)

    # Double Escape
    DElist = {}
    for i, iso in enumerate(g.IsotopeData):         # iso is key like K-40
        if iso in getIsotopeData:
            for isoen in g.IsotopeData[iso]:
                if isoen < 1022: continue
                if g.plotLineDoubleEscape:  DElist.update({isoen - 1022  : iso + " DE"})
    DEsort = dict(sorted(DElist.items(), reverse=True, key=lambda item: item[0]))
    GammaList.update(DEsort)

    # Back Scatter
    BSlist = {}
    for i, iso in enumerate(g.IsotopeData):         # iso is key like K-40
        if iso in getIsotopeData:
            for isoen in g.IsotopeData[iso]:
                BSengy = isoen - getComptonEdge(isoen)
                if g.plotLineBackScatter:  BSlist.update({BSengy  : iso + " BS"})
    BSsort = dict(sorted(BSlist.items(), reverse=True, key=lambda item: item[0]))
    GammaList.update(BSsort)

    ### print to terminal
    cdprint(defname, "Photopeak")
    for i, gs in enumerate(PHsort): cdprint(defname, f"Photo Peak:    i:{i:3d} {gs:9.3f}   PH   {PHsort[gs]}")

    if len(CEsort) == 0:    cdprint(defname, "Compton Edge   - not requested")
    else:                   cdprint(defname, "Compton Edge")
    for i, gs in enumerate(CEsort): cdprint(defname, f"Compton Edge:  i:{i:3d} {gs:9.3f}   CE   {CEsort[gs]}")

    if len(SEsort) == 0:    cdprint(defname, "Single Escape  - not requested")
    else:                   cdprint(defname, "Single Escape")
    for i, gs in enumerate(SEsort): cdprint(defname, f"Single Escape: i:{i:3d} {gs:9.3f}   SE   {SEsort[gs]}")

    if len(DEsort) == 0:    cdprint(defname, "Double Escape  - not requested")
    else:                   cdprint(defname, "Double Escape")
    for i, gs in enumerate(DEsort): cdprint(defname, f"Double Escap i:{i:3d} {gs:9.3f}   SE   {DEsort[gs]}")

    if len(BSsort) == 0:    cdprint(defname, "Back Scatter   - not requested")
    else:                   cdprint(defname, "Back Scatter")
    for i, gs in enumerate(BSsort): cdprint(defname, f"Back Scatter:  i:{i:3d} {gs:9.3f}   BS   {BSsort[gs]}")

    # print to terminal as sorted list over all gammas
    cdprint(defname, "Combined Gamma Lines")
    for i, gs in enumerate(GammaList):
        if   "CE" in GammaList[gs]: type = "CE"
        elif "SE" in GammaList[gs]: type = "SE"
        elif "DE" in GammaList[gs]: type = "DE"
        elif "BS" in GammaList[gs]: type = "BS"
        else:                       type = "PP"
        cdprint(defname, f"GammaList:     i:{i:3d} {gs:9.3f}   {type}   {GammaList[gs]}")
    dprint("")

    for i, isoenergy in enumerate(GammaList):
        isoname     = GammaList[isoenergy]
        isochannel  = getChannel(isoenergy)
        imsg        = f"i:{i:3d}  Nam {isoname:10s} Energy: {isoenergy:8.3f}  Channel#: {isochannel:4d}  "
        mdprint(defname, f"imsg: {imsg}")

        # find which delta is giving best r2
        maxr2     = [0, 0]
        for delta in range(10, 151, 10):
            dr2 = getR2FromGaussFit(isoname, isoenergy, isochannel, delta, imsg)
            if dr2 > maxr2[1]:    maxr2 = [delta, dr2]

        delta = maxr2[0]
        if delta > 0:  getFitForDelta(isoname, isoenergy, isochannel, delta, imsg)
        else:          mdprint(defname, f"No fit found")

    sprint("")
    setNormalCursor()
    setIndent(0)


def getR2FromGaussFit(isoname, isoenergy, isochannel, delta, imsg):
    """"""

    defname = "getR2FromGaussFit: "

    left  = max(isochannel - delta, 0)                          # left side must be channel >= 0
    right = min(isochannel + delta, len(g.EnergyCalib) - 1)     # right side must be less than max channel

    fitEn   = g.EnergyCalib [left : right]
    fitCn   = g.Counts      [left : right]

    # set and remove background
    fitBg = np.linspace(fitCn[0], fitCn[-1], len(fitCn))
    fitCn = fitCn.copy() - fitBg

    ### Fit
    peak  = max(10, np.max(fitCn))
    mean  = isoenergy
    sigma = 10
    try:
        _, fitr2 = getGaussFit(fitEn, fitCn, peak, mean, sigma)
        mdprint(defname, f"Fit r2: {fitr2:9.3f}  at delta: {delta}")
    except Exception as e:
        exceptPrint(e, f"Gauss Fit Failure {isoname:10s} Energy: {isoenergy:8.3f} Delta: {delta}")
        fitr2 = g.NAN

    return fitr2


def getFitForDelta(isoname, isoenergy, isochannel, delta, imsg):
    """"""

    defname = "getFitForDelta: "

    # dprint(defname, f"isonam {isoname}  isoenergy: {isoenergy}  isochannel: {isochannel}, delta: {delta}  imsg: {imsg}")

    left  = max(isochannel - delta, 0)                          # left side must be channel >= 0
    right = min(isochannel + delta, len(g.EnergyCalib) - 1)     # right side must be less than max channel

    newdelta = right - left

    fitEn   = g.EnergyCalib[left : right]
    fitCn   = g.Counts[left : right]
    # dprint(defname, f"fitEn: len: {len(fitEn)}  \n{fitEn}")
    # dprint(defname, f"fitCn: len: {len(fitCn)}  \n{fitCn}")

    # set background
    fitBg = np.linspace(fitCn[0], fitCn[-1], len(fitCn))
    fitCn = fitCn.copy() - fitBg
    # mdprint(defname, f"E left: {left}  E right: {right}   len(fitEn): {len(fitEn)}")

    ###
    ### Fit
    ###
    peak  = max(10, np.max(fitCn))
    mean  = isoenergy
    sigma = 10
    try:
        response, fitr2 = getGaussFit(fitEn, fitCn, peak, mean, sigma)
    except Exception as e:
        exceptPrint(e, f"Failure getting Gauss fit for {isoname:10s} Energy: {isoenergy:8.3f} ")
        return g.NAN

    # irdprint(defname, f"respons {response}")
    if response != "Failure":
        popt        = response[0]
        # PCOV      = response[1]
        # fitinfo   = response[2]   # what to do with it? ignore it
        # fitmsg    = response[3]   # So far was always: "Both actual and predicted relative reductions in the sum of squares are at most 0.000000"
        # fitFlag     = response[4]
        fitHeight   = popt[0]
        fitEnergy   = popt[1]       # of peak
        fitSigma    = popt[2]       # of peak

        # negative sigma
        if fitSigma < 0:
            msg = f"FITenergy: {fitEnergy:8.3f}  Channels: {newdelta:3d}  Fitr2: {'N.A.'}  Sigma NEGATIVE"
            rdprint(defname, imsg + msg)
            return g.NAN

        # good / bad r2
        if fitr2 >= 0.5:
            msg = f"FITenergy: {fitEnergy:8.3f}  Channels: {newdelta:3d}  Fitr2: {fitr2:0.3f}"
            gdprint(defname, imsg + msg)

            sresult         = Gauss(fitEn, *popt)
            fwhmA           = fitSigma * 2.3548       # FWHM in keV
            fwhmP           = fwhmA / fitEnergy       # FWHM in percent
            deltaE          = isoenergy - fitEnergy   # delta of expected and found energy
            deltaEpc        = deltaE / fitEnergy
            deltaChnl       = len(fitEn)
            msg             = f"{isoname:10s}{isoenergy:8.3f} : {fitEnergy:8.3f} {deltaEpc:8.1%}  {fwhmA:7.2f} {fwhmP:7.2%} {fitr2:5.3f} {deltaChnl:5.0f}"

            if (abs(deltaE)) < (0.1 * isoenergy):     # are energies true and fit within 10%?
                sprint(msg)
                for i in range(len(fitEn)):
                    fqchannel = isochannel + i - len(fitEn) // 2
                    # irdprint(defname, f"isochannel: {isochannel}  fqchannel: {fqchannel}  left:{left}  len(fitEn): {len(fitEn)}")

                    # wenn fitQuality==NAN (=nix drin) dann add peak und BG
                    if np.isnan(g.fitQuality[fqchannel]): g.fitQuality[fqchannel] = sresult[i] + fitBg[i]
                    else:                              g.fitQuality[fqchannel] = max(g.fitQuality[fqchannel], sresult[i] + fitBg[i])

        else:
            msg = f"FITenergy: {fitEnergy:8.3f}  Channels: {delta:3d}  Fitr2: {fitr2:0.3f}"
            rdprint(defname, imsg + msg)


#ps
def plotGraphSpectro():

    global sax1, sax2

    defname = gd(sys._getframe().f_code.co_name)

    # sprint(defname + f"at start: fignums: {plt.get_fignums()}")

    # clear old graph - is required!
    plt.clf()

    ### get/set left and right Y-axis
    sax1 = plt.gca()                           # left Y-axis
    sax2 = sax1.twinx()                        # right Y-Axis

    # add labels to axis
    sax1.set_ylabel("Counts",  fontsize=12, fontweight='bold')                     # Yleft-axis

    plotLegendSpectro()

    # thickness of symbols (Only used for Spectrum Calibrated)
    try:
        msize = 1.5 * 60 / np.sqrt(len(g.clipEnergy))   # size for '.' as plot symbol
    except Exception as e:
        exceptPrint(e, defname + "markersize")
        msize = 3

    # to prevent scientific notation and offset use
    sax2.yaxis.get_major_formatter().set_scientific(False)      # science
    sax2.yaxis.get_major_formatter().set_useOffset(False)       # offset
    sax2.ticklabel_format(style='plain', axis='y')              # do NOT use scientific notation

    sax1.yaxis.get_major_formatter().set_scientific(False)
    sax1.yaxis.get_major_formatter().set_useOffset(False)
    sax1.ticklabel_format(style='plain', axis='y')

    # Energy as X-Axis
    # label
    sax1.set_xlabel("Energy [keV]",       fontsize=12, fontweight='bold')         # X-axis
    sax2.set_ylabel("Channel Width [eV]", fontsize=12, fontweight='bold')         # Yright-axis

    # r2 shown in bottom left of graph
    if g.spectroShowFit:
        mean = g.fitCoeff[1]
        FWHM = g.fitCoeff[2] * 2.3548
        fittext = f"Fit r2: {g.spectroGaussFitR2:0.3f}  FWHM: {FWHM / mean:0.1%}"
        plt.figtext(0.01, 0.02, fittext,      fontsize=13, fontweight=1000)

    ### set title -  a plt.suptitle is a "SUPER" title, not a sub title  ;-)
    RightTitle = os.path.basename(g.spectroDBPath) + f"  Chnls: {len(g.clipEnergy)} of {g.spectroDataLen}"
    plt.title(RightTitle, fontsize=10, fontweight='normal', loc = 'right')

    plotGammaLines(max(g.clipCounts))

    fitcol = getFitColorPlot(g.spectroGaussFitR2)

    if g.spectroShowSearchPeak:
        FScolor = "#73D216" # hellgrün
        sax1.plot(g.clipEnergyCalib,         psScale(g.clipfitQuality), "-",  color=FScolor, alpha=0.8, lw=6.5,   label="FitSearch")

        # Filling  -   Dieser Fill sollte zwischen Peak und Background sein, aber BG gibt es nicht!
        # sax1.fill_between(g.clipEnergy, psScale(g.clipfitQuality),       color=FScolor, alpha=0.3)


    if g.spectroShowFit and len(g.clipFitEnergy) > 0:
        frenergy                = np.arange(g.clipFitEnergy[0], g.clipFitEnergy[-1], 0.01)
        plotspectroBackground   = np.linspace(g.spectroBackgroundLimits[0], g.spectroBackgroundLimits[1], len(frenergy))
        pfitResult              = Gauss(frenergy, *g.fitCoeff) #+ plotspectroBackground

        # check for matching current Energy limits
        newfrenergy   = []
        newpfitResult = []
        newplotBG     = []
        for i in range(len(frenergy)):
            if frenergy[i] >= g.clipEnergyCalib[0] and frenergy[i] <= g.clipEnergyCalib[-1]:
                newfrenergy  .append(frenergy[i])
                newpfitResult.append(pfitResult[i])
                newplotBG    .append(plotspectroBackground[i])

        npnewfrenergy   = np.array(newfrenergy)
        npnewpfitResult = np.array(newpfitResult)
        npnewplotBG     = np.array(newplotBG)
        if len(newpfitResult) > 0:
            x   = npnewfrenergy
            y   = psScale(npnewpfitResult + npnewplotBG)
            yBG = psScale(npnewplotBG)
            sax1.plot(x,  y,                                       "-", color=fitcol, alpha=1.0, lw=4.0, label="Fit")
            sax1.fill_between(x, y, yBG,                                color=fitcol, alpha=0.3)

    try:
        # Energy on X-axis
        # Grid
        if g.spectroShowGrid:       # grid for left Y
            sax1.grid(visible=True, which='both', axis="both")
            sax1.grid(which='minor', color='#999', linestyle=':', lw=0.5)
            sax1.minorticks_on()

        # right y
        if g.spectroShowChnlW:  sax2.plot(g.clipEnergyCalib, g.clipChnlWidthFit * 1E3, "-",  color="brown", lw=6, alpha=0.5,  label="Channel Width")
        if g.spectroShowOrig:   sax2.plot(g.clipEnergyCalib, g.clipChWidth * 1E3,      "--", color="brown", lw=2,             label="Channel Width Orig")

        yRbottom, yRtop = sax2.get_ylim()
        if yRbottom > 0: sax2.set_ylim(bottom=0, top=yRtop * 1.1)

        # left y -  counts vs energy
        if g.spectroShowLine: lw, symbol = 0.5, ".-"
        else:                 lw, symbol = 0.0, "."
        sax1.plot(g.clipEnergyCalib,  psScale(g.clipCounts),  symbol, color="blue",    lw=lw, label="Spectrum", markersize=msize)

    except Exception as e:
        exceptPrint(e, defname + "xy-plots" )

    if g.figSpectro is not None: pushPlotToScreen(g.figSpectro)


def psScale(data):
    """Plot the data as Lin or Log"""

    defname = "psScal "

    newdata  = data.copy()
    newlabel = "Counts"

    if g.spectroShowLog:
        newlabel = "Log(Counts)"
        try:    newdata  = np.log10(data)
        except: ydprint(defname, "Failure to get 'np.log10(data)'")

    sax1.set_ylabel(newlabel, fontsize=12, fontweight='bold')       # label Yleft-axis

    return newdata


def plotGammaLines(maxY):

    defname = gd(sys._getframe().f_code.co_name)

    ### draw gamma energies K-40, Co-60, ...
    if 1:

        isotopes = g.spectroGammaSelection
        if len(isotopes) == 0:
            pass                # do nothing as no isotopes selected

        else:
            # irdprint(defname, "isotopes: ", isotopes)

            icolor  = "#00ff00" # green     main isotope line
            CEcolor = "orange"    # orange    Compton Edge
            SEcolor = "#F57900" # reddish   Single Escape
            DEcolor = "#8F5902" # brownish  Double Escape
            BScolor = "#333333" # grey      Backscatter

            gammamin = -1 * max(0.08 * psScale(maxY), 0)                  # 8% der Scale; assuming bottom is zero
            gammamax = np.max(g.clipCounts)
            # irdprint(defname, f"gammamin: {gammamin} maxY: {maxY}    gammamax: {gammamax} ")

            plotmin  = gammamin
            plotmax  = psScale(gammamax) * 1.7               # make space above highest Counts to allow the text for the isotope line
            sax1.set_ylim(bottom=plotmin, top=plotmax)

            for isotope in isotopes:
                cdprint(defname, f"isotop {isotope}")
                if isotope in ("Compton Edge", "Single Escape", "Double Escape", "Back Scatter"):    continue

                # get the list of energies for each isotope
                try:
                    Engs = g.IsotopeData[isotope]
                    # cdprint(defname, f"Isotop  {isotop8s}  Engs: {Engs}")
                except Exception as e:
                    exceptPrint(e, defname)
                    continue

                # take each energy of that isotope
                for Eng in Engs:
                    Eng = round(Eng, 3)
                    if Eng >= g.spectroLeftClipEnergy and Eng <= g.spectroRightClipEnergy:
                        # irdprint(defname, "Plotting Main Peak")
                        sax1.text(Eng, plotmax * 0.98, f"{isotope}  {Eng:0.7g}" , fontsize=9.0, rotation=270, ha="left", va="top", fontweight=500)
                        sax1.plot([Eng, Eng], [plotmin, plotmax * 0.98], "-", color=icolor,    lw=1.5, label=isotope)

                    if g.plotLineComptonEdge:
                        # irdprint(defname, "Plotting CE")
                        EngCE = getComptonEdge(Eng)
                        if EngCE >= g.spectroLeftClipEnergy and EngCE <= g.spectroRightClipEnergy:
                            sax1.text(EngCE, plotmax * 0.98, f"{isotope + ' CE'}  {EngCE:0.2f}" , fontsize=9.0, rotation=270, ha="left", va="top", fontweight=500)
                            sax1.plot([EngCE, EngCE], [plotmin, plotmax * 0.98], "-", color=CEcolor,    lw=1.5, label=isotope)

                    if g.plotLineSingleEscape:
                        # irdprint(defname, "Plotting SE")
                        if Eng >= 1022:
                            EngSE = Eng - 511
                            if EngSE >= g.spectroLeftClipEnergy and EngSE <= g.spectroRightClipEnergy:
                                sax1.text(EngSE, plotmax * 0.98, f"{isotope + ' SE'}  {EngSE:0.2f}" , fontsize=9.0, rotation=270, ha="left", va="top", fontweight=500)
                                sax1.plot([EngSE, EngSE], [plotmin, plotmax * 0.98], "--", color=SEcolor,    lw=1.5, label=isotope)

                    if g.plotLineDoubleEscape:
                        # irdprint(defname, "Plotting DE")
                        if Eng >= 1022:
                            EngDE = Eng - 1022
                            if EngDE >= g.spectroLeftClipEnergy and EngDE <= g.spectroRightClipEnergy:
                                sax1.text(EngDE, plotmax * 0.98, f"{isotope + ' DE'}  {EngDE:0.2f}" , fontsize=9.0, rotation=270, ha="left", va="top", fontweight=500)
                                sax1.plot([EngDE, EngDE], [plotmin, plotmax * 0.98], ":", color=DEcolor,    lw=1.5, label=isotope)

                    if g.plotLineBackScatter:
                        # irdprint(defname, "Plotting BS")
                        EngBS = Eng - getComptonEdge(Eng)
                        if EngBS >= g.spectroLeftClipEnergy and EngBS <= g.spectroRightClipEnergy:
                            sax1.text(EngBS, plotmax * 0.98, f"{isotope + ' BS'}  {EngBS:0.2f}" , fontsize=9.0, rotation=270, ha="left", va="top", fontweight=500)
                            sax1.plot([EngBS, EngBS], [plotmin, plotmax * 0.98], ":", color=BScolor,    lw=1.5, label=isotope)


def plotLegendSpectro():
    #
    # Plot the Legend
    #
    ## best place for Legend found with "best" (is default anyway) -  gives "Warning": using "best" could take long with many data
    ## supported values are 'best', 'upper right', 'upper left', 'lower left', 'lower right', 'right',
    ##                      'center left', 'center right', 'lower center', 'upper center', 'center'
    ## ax1.legend(loc="upper left",   fontsize=10, prop={"family":"monospace"})  # is covering too much of plot area
    ## ax2.legend(loc="upper right",  fontsize=10, prop={"family":"monospace"})  # dito
    #
    # fc: facecolor
    # ec: edgecolor
    # #FCE94F is yellowish

    pp  = ()
    pl  = ()

    p   = plt.Rectangle((0, 0), 1.0, 1.0, fc="blue",    ec="black", lw=0.2)
    pp += (p,)
    pl += ("Spectrum",)

    p   = plt.Rectangle((0, 0), 1.0, 1.0, fc="#00ff00", ec="red",   lw=2.5)
    pp += (p,)
    pl += ("Fit",)

    # spacer
    p   = plt.Rectangle((0, 0), 0.0, 0.0, fc="#C9F9F0",   ec="#C9F9F0", lw=0.2)
    pp += (p,)
    pl += ("",)

    # spacer
    p   = plt.Rectangle((0, 0), 0.0, 0.0, fc="#C9F9F0",   ec="#C9F9F0", lw=0.2)
    pp += (p,)
    pl += ("",)

    # spacer
    p   = plt.Rectangle((0, 0), 0.0, 0.0, fc="#C9F9F0",   ec="#C9F9F0", lw=0.2)
    pp += (p,)
    pl += ("",)

    # spacer
    p   = plt.Rectangle((0, 0), 0.0, 0.0, fc="#C9F9F0",   ec="#C9F9F0", lw=0.2)
    pp += (p,)
    pl += ("",)

    p   = plt.Rectangle((0, 0), 1.0, 1.0, fc="#D19494",   ec="black", lw=0.2)
    pp += (p,)
    pl += ("WidthCalib",)

    p   = plt.Rectangle((0, 0), 1.0, 1.0, fc="brown",     ec="black", lw=0.2)
    pp += (p,)
    pl += ("WidthOrig",)

    plt.figlegend(pp, pl, shadow=False, mode="expand", handlelength=1.6, ncol=8, framealpha=0)


def sprint(text=""):
    """Append text to Spectro NotePad"""
    ### CAUTION: Fails when g.spectroNotePad is None!!!

    defname = "sprint: "
    try:
        if g.spectroNotePad is not None:
            g.spectroNotePad.append(text)
            g.spectroNotePad.moveCursor (QTextCursor.MoveOperation.End)
    except Exception as e:
        exceptPrint(e, defname)


def esprint(text=""):
    """Append text to Spectro NotePad in red ERROR color"""

    defname = "sprint: "

    newtext  = f"<span style='color:red;  '>{text}</span>"
    newtext += f"<span style='color:black;'>&nbsp;</span>" # MUST print anything but space to reset color

    try:
        if g.spectroNotePad is not None:
            g.spectroNotePad.append(newtext)
            g.spectroNotePad.moveCursor (QTextCursor.MoveOperation.End)
            burp()
    except Exception as e:
        exceptPrint(e, defname)


def clearNotePad():
    g.spectroNotePad.setText("")


def printFitResult():

    defname = "printFitResult: "

    try:
        if g.spectroShowFit:
            sprint(headerSpec("Fit Peak"))
            if g.fitSuccess:

                comptonEdge  = getComptonEdge(g.spectroMean)  # get single value for Gamma=g.spectroMean
                comptonDelta = g.spectroMean - comptonEdge
                sigma        = g.spectroSigma
                FWHM         = 2.3548 * sigma
                relFWHM      = FWHM / g.spectroMean

                countsresult = 0
                countsclip   = 0
                energyPeak   = 0
                for i in range(len(g.clipFitCounts)):
                    rf = g.fitResult[i]
                    countsresult += rf
                    countsclip   += g.clipFitCounts[i]
                    chenergy      = rf * g.clipFitEnergy[i]
                    energyPeak   += chenergy
                    # mdprint(defname, f"rf: {rf:8.2f}  cnts: {clipFitCounts[i]:8.2f} Enrgy: {clipFitEnergy[i]:8,.2f} chEn: {chenergy:8,.0f}  En: {energyPeak:8,.0f}")

                ### for Peaktotal se g.spectroPeak * np.sqrt( np.pi * g.spectroSigma * 2)  # se https://en.wikipedia.org/wiki/Gaussian_integral
                sprint(f"Calibration : {g.spectroScale}")
                sprint(f"Energy [keV]: {g.spectroMean  :7.2f}  Compton Edge: {comptonEdge:0.0f}  Back Scatter: {comptonDelta:0.0f}  ChnlWdth: {getChannelWidth(g.spectroMean):0.2f}")
                sprint(f"FWHM   [keV]: {FWHM  :7.2f}  {relFWHM:0.2%} of Energy")
                if g.debug:
                    sprint(f"Sigma  [keV]: {sigma :7.2f}  {sigma/g.spectroMean:0.2%} of Energy")
                sprint(f"Peak Height : {g.spectroPeak:0.2f} Counts   Half Height: {g.spectroPeak / 2.0:0.2f} Counts")
                sprint(f"Peak Totals : Counts: {countsclip:0.0f}    Energy: {energyPeak / 1000:<0,.0f} MeV")
                sprint(f"Fit Props   : Channels: {len(g.clipFitCounts)}  Method: '{g.spectroFitMethod}'")
                sprint("")

            else:
                sprint(f"Failure (Lack-of-Fit)\n")

    except Exception as e:
        exceptPrint(e, defname)


def clipSpectrumData():
    """make data by clipping left and right; all spectra EXCEPT As-is"""

    defname = "clipSpectrumData: "
    # ydprint(defname)

    # right side - maximum energy
    try:
        g.spectroMaxE = g.EnergyCalib.max()
    except Exception as e:
        exceptPrint(e, defname)
        g.spectroMaxE = +10000
    if g.spectroRightClipEnergy > g.spectroMaxE: g.spectroRightClipEnergy = g.spectroMaxE
    if g.spectroRightFitEnergy  > g.spectroMaxE: g.spectroRightFitEnergy  = g.spectroMaxE

    # left side - minimum energy
    try:
        g.spectroMinE = g.EnergyCalib.min()
    except Exception as e:
        exceptPrint(e, defname)
        # g.spectroMinE = 0
        g.spectroMinE = -10000
    if g.spectroLeftClipEnergy < g.spectroMinE: g.spectroLeftClipEnergy = g.spectroMinE
    if g.spectroLeftFitEnergy  < g.spectroMinE: g.spectroLeftFitEnergy  = g.spectroMinE

    # ydprint(defname, f"g.spectroMaxE: {g.spectroMaxE}  g.spectroMinE: {g.spectroMinE}  ")

    # fillEnergyBoxes()

    # 07 13:20:34.235 DEVEL  : ...501 printArrays: clipSpectrumData: -------------------------------------------
    # 07 13:20:34.235 DEVEL  : ...502 printArrays: Energy:          1800
    # 07 13:20:34.235 DEVEL  : ...503 printArrays: Counts:          1800
    # 07 13:20:34.235 DEVEL  : ...504 printArrays: EnergyCalib:     1800
    # 07 13:20:34.235 DEVEL  : ...505 printArrays: clipEnergy:      1712
    # 07 13:20:34.235 DEVEL  : ...506 printArrays: clipCounts:      1712
    # 07 13:20:34.236 DEVEL  : ...507 printArrays: clipFitEnergy:   1712
    # 07 13:20:34.236 DEVEL  : ...508 printArrays: clipFitCounts:   1800
    # 07 13:20:34.236 DEVEL  : ...509 printArrays: clipEnergyCalib: 1712
    # 07 13:20:34.236 DEVEL  : ...510 printArrays: ChnlWidthOrig:   1800
    # 07 13:24:37.831 DEVEL  : ...512 printArrays: clipChnlWidthFit:1712
    # 07 13:22:38.495 DEVEL  : ...511 printArrays: ChnlWidthCalib:  1800
    # 07 13:20:34.236 DEVEL  : ...511 printArrays: clipChWidth:     1712
    # 07 13:20:34.236 DEVEL  : ...512 printArrays: fitresult:       1800
    # 07 13:20:34.236 DEVEL  : ...513 printArrays: fitqual:         1800

    try:
        # printArrays(defname)

        clipEnergy, clipEnergyCalib, clipCounts, clipChWidth, clipChnlWidthFit, clipQual, clipFitEnergy  = [], [], [], [], [], [], []

        for i in range(0, g.spectroDataLen - g.spectroCumul + 1, g.spectroCumul):
            if g.EnergyCalib[i] >= g.spectroLeftClipEnergy  and g.EnergyCalib[i] <= g.spectroRightClipEnergy :
                en, co, cw, CWF, fqual, CEF, CFE = 0, 0, 0, 0, 0, 0, 0
                for j in range(g.spectroCumul):
                    en      += g.EnergyOrig         [i + j] # 1800 --> clipEnergy       : 1712
                    CEF     += g.EnergyCalib        [i + j] # 1800 --> clipEnergyCalib  : 1712
                    co      += g.Counts             [i + j] # 1800 --> clipCounts       : 1712
                    cw      += g.ChnlWidthOrig      [i + j] # 1800 --> clipChWidth      : 1712
                    CWF     += g.ChnlWidthCalib     [i + j] # 1800 --> clipChnlWidthFit : 1712
                    fqual   += g.fitQuality         [i + j]
                    # CFE     += g.clipFitEnergy    [i + j] # 1712 --> Failure
                    CFE     += g.NAN

                clipEnergy      .append(en     / g.spectroCumul)
                clipEnergyCalib .append(CEF    / g.spectroCumul)

                clipCounts      .append(co)
                clipChWidth     .append(cw     / g.spectroCumul)
                clipChnlWidthFit.append(CWF    / g.spectroCumul)
                clipQual        .append(fqual  / g.spectroCumul)
                # clipFitEnergy   .append(CFE    / g.spectroCumul)
            # else:
            #     ydprint(defname, f"Failure to account for: i: {i}  g.EnergyCalib[i]: {g.EnergyCalib[i]}  g.spectroLeftClipEnergy:{g.spectroLeftClipEnergy}")

        g.clipEnergy        = np.array(clipEnergy)
        g.clipEnergyCalib   = np.array(clipEnergyCalib)
        g.clipCounts        = np.array(clipCounts)
        g.clipChWidth       = np.array(clipChWidth)
        g.clipChnlWidthFit  = np.array(clipChnlWidthFit)
        g.clipfitQuality       = np.array(clipQual)
        # g.clipFitEnergy     = np.array(clipFitEnergy)

        # ydprint(defname, f"i: {i} g.EnergyOrig:    len: {len(g.EnergyOrig)}  {g.EnergyOrig[:3]}...{g.EnergyOrig[-3:]}")
        # ydprint(defname, f"i: {i} g.EnergyCalib:   len: {len(g.EnergyCalib)}  {g.EnergyCalib[:3]}...{g.EnergyCalib[-3:]}")
        # ydprint(defname, f"i: {i} g.clipEnergy:    len: {len(g.clipEnergy)}  {g.clipEnergy[:3]}...{g.clipEnergy[-3:]}")
        # ydprint(defname, f"i: {i} clipEnergyCalib: len: {len(g.clipEnergyCalib)}  {g.clipEnergyCalib[:3]}...{g.clipEnergyCalib[-3:]}")

    except Exception as e:
        exceptPrint(e, defname)
        ydprint(defname, f"i: {i} g.clipFitEnergy: {g.clipFitEnergy}  len: {len(g.clipFitEnergy)}")
        ydprint(defname, f"i: {i} g.EnergyOrig:    {g.EnergyOrig}     len: {len(g.EnergyOrig)}")
        ydprint(defname, f"i: {i} g.EnergyCalib:   {g.EnergyCalib}    len: {len(g.EnergyCalib)}")
        printArrays(defname)


def headerSpec(txt, size=68):
    """position txt within '==...==' string"""

    return "==== {} {}".format(txt, "=" * max(1, (size - len(txt))))

#update
def updateEditBoxes():

    defname = "updateEditBoxes: "

    try:
        clipSpectrumData()

        g.spectroLeftClipBox .setText(f"{g.spectroLeftClipEnergy    :0,.2f}")
        g.spectroRightClipBox.setText(f"{g.spectroRightClipEnergy   :0,.2f}")

        g.spectroLeftFitBox .setText(f"{g.spectroLeftFitEnergy      :0,.2f}")
        g.spectroRightFitBox.setText(f"{g.spectroRightFitEnergy     :0,.2f}")

        g.channelNumbers    .setText(f"{len(g.clipEnergy)           :0,.0f}")
        g.countNumbers      .setText(f"{np.sum(g.clipCounts)        :0,.7g}")

        g.channelFitNumbers .setText(f"{len(g.clipFitEnergy)        :0,.0f}")
        g.countFitNumbers   .setText(f"{np.sum(g.fitResult)     :0,.7g}")

    except Exception as e:
        exceptPrint(e, defname)


def printSpectroInfo():
    """Print Spectro database Metadata into Spectro NotePad"""

    msg  = headerSpec("Info") + "\n"
    msg += getSpectroInfo()
    sprint(msg)


def printSpectroData():
    """Print database data into Spectro NotePad"""

    msg  = headerSpec("Graph-Data") + "\n"
    msg += getSpectroGraphDataAll()
    sprint(msg)


def getChannel(gamma):
    """Find the Channel for a given gamma energy"""

    for i in range(len(g.EnergyCalib)):
        # mdprint(f"i: {i}   g.EnergyCalib[i]: {g.EnergyCalib[i]:10.4f}  gamma: {gamma}")
        if gamma <= g.EnergyCalib[i]: return i

    return i


def getChannelWidth(gamma):
    """Find the Channel width for a given gamma energy"""

    for i in range(len(g.EnergyCalib)):
        if gamma < g.EnergyCalib[i]: continue
        return g.ChnlWidthCalib[i]

    return g.NAN


def printArrays(source):

    defname = "printArrays: "

    cdprint(defname, source, "-------------------------------------------")

    cdprint(defname, f"Energy:            {len(g.EnergyOrig)        }     ")
    cdprint(defname, f"Counts:            {len(g.Counts)            }     ")

    cdprint(defname, f"EnergyCalib:       {len(g.EnergyCalib)       }     ")

    cdprint(defname, f"clipEnergy:        {len(g.clipEnergy)        }     ")
    cdprint(defname, f"clipCounts:        {len(g.clipCounts)        }     ")

    cdprint(defname, f"clipFitEnergy:     {len(g.clipFitEnergy)     }     ")
    cdprint(defname, f"clipFitCounts:     {len(g.clipFitCounts)     }     ")

    cdprint(defname, f"clipEnergyCalib:   {len(g.clipEnergyCalib)   }     ")

    cdprint(defname, f"ChnlWidthOrig:     {len(g.ChnlWidthOrig)     }     ")
    cdprint(defname, f"ChnlWidthCalib:    {len(g.ChnlWidthCalib)    }     ")
    cdprint(defname, f"clipChnlWidthFit:  {len(g.clipChnlWidthFit)  }     ")
    cdprint(defname, f"clipChWidth:       {len(g.clipChWidth)       }     ")
    cdprint(defname, f"clipChWidth:       {len(g.clipChWidth)       }     ")

    cdprint(defname, f"fitresult:         {len(g.fitResult)         }     ")
    cdprint(defname, f"fitqual:           {len(g.fitQuality)        }     ")


##########################################################
def resetSpectroParams():
    g.spectroCumul              = 1

    g.spectroLeftClipEnergy     = -10000
    g.spectroRightClipEnergy    = +10000
    g.spectroLeftFitEnergy      = -10000
    g.spectroRightFitEnergy     = +10000

    # g.spectroShowSpec           = True
    g.spectroShowFit            = False
    g.spectroShowSearchPeak     = False
    g.spectroShowOrig           = False

    g.spectroShowGrid           = True
    g.spectroShowLog            = False
    g.spectroShowLine           = True

    g.spectroNotePadtxt         = ""
    g.spectroGamma4Compton      = 0

    g.spectroScale              = g.spectroScaleOrig.copy()
    for i in range(g.spectroDataLen):       g.EnergyCalib[i]       = calibChannelToEnergy(i)
    for i in range(g.spectroDataLen - 1):   g.ChnlWidthCalib[i]    = g.EnergyCalib[i + 1] - g.EnergyCalib[i]

    g.calibFitResult    = None

    g.calibLeft         = [None,   None]
    g.calibRight        = [None,   None]
    g.calibLeftFit      = [None,   None]
    g.calibRightFit     = [None,   None]

    g.fitResult           = np.full(len(g.fitResult), g.NAN)

    g.calibShowEW         = False
    g.calibShowOrig       = False

##########################################################


class NavigationToolbar(NavigationToolbar):
    #  https://stackoverflow.com/questions/12695678/how-to-modify-the-navigation-toolbar-easily-in-a-matplotlib-figure-window

    # None of the tools
    toolitems = []

    # all of them
    # toolitems = [t for t in NavigationToolbar.toolitems if t[0] in ('Home', 'Back', 'Forward', 'Backward', 'Pan', 'Zoom', 'Subplots', 'Customize', 'Save')]

    # only display the buttons we need
    # toolitems = [t for t in NavigationToolbar.toolitems if t[0] in ('Home', 'Back', 'Forward', 'Backward', 'Pan', 'Zoom', 'Customize')]
    # toolitems = [t for t in NavigationToolbar.toolitems if t[0] in ('Home', 'Back', 'Forward', 'Customize')]


def selectIsotopes(selectall=False):
    """Select one or more isotopes for fitting and plotting"""

    defname = gd(sys._getframe().f_code.co_name)

    Gammaheader = QLabel(f"{' Isotope':15s}      Gamma-Energies [keV]")
    Gammaheader.setFont(g.fontstd)

    GammaList = QListWidget()
    GammaList.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
    GammaList.setToolTip('Select one or more isotopes')
    GammaList.setMinimumHeight(600)
    GammaList.setMinimumWidth (750)
    GammaList.setFont(g.fontstd)

    for iso in list(g.IsotopeData.items()):
        # mdprint(defname, "iso: ", iso)                                                          # iso == ('K-40', [1460.81])
        Sitem = QListWidgetItem(f"{iso[0]:17s} : {g.IsotopeData[iso[0]]}")
        GammaList.addItem(Sitem)
        if iso[0] in g.spectroGammaSelection:                   GammaList.setCurrentItem(Sitem)
        if iso[0] == "Compton Edge"  and g.plotLineComptonEdge:  GammaList.setCurrentItem(Sitem)
        if iso[0] == "Single Escape" and g.plotLineSingleEscape: GammaList.setCurrentItem(Sitem)
        if iso[0] == "Double Escape" and g.plotLineDoubleEscape: GammaList.setCurrentItem(Sitem)
        if iso[0] == "Back Scatter"  and g.plotLineBackScatter:  GammaList.setCurrentItem(Sitem)


    PrintGammabButton = QPushButton("Print")
    PrintGammabButton.setStyleSheet("QPushButton")
    PrintGammabButton.setAutoDefault(False)
    PrintGammabButton.setToolTip("Print Gamma Energies to Notepad")
    PrintGammabButton.clicked.connect(lambda:  printGammaLines())

    bbox = QDialogButtonBox()
    bbox.setStandardButtons          (QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok )
    bbox.addButton(PrintGammabButton, QDialogButtonBox.ButtonRole.ActionRole)
    bbox.accepted.connect(lambda: dlg.done(100))
    bbox.rejected.connect(lambda: dlg.done(0))

    dlg = QDialog() # set parent to None to popup in center of screen
    dlg.setWindowIcon(g.iconGeigerLog)
    dlg.setFont(g.fontstd)
    dlg.setWindowTitle("Select Isotopes for Fitting and Plotting")
    # dlg.setWindowModality(Qt.WindowModality.NonModal)
    dlg.setWindowModality(Qt.WindowModality.WindowModal)

    layoutV = QVBoxLayout(dlg)
    layoutV.addWidget(QLabel("Select one or more entries"))
    layoutV.addWidget(Gammaheader)
    layoutV.addWidget(GammaList)
    layoutV.addWidget(bbox)

    retval = dlg.exec()
    # print("retval:", retval)

    if retval == 0:
        pass

    elif retval == 100:

        g.plotLineComptonEdge  = False
        g.plotLineSingleEscape = False
        g.plotLineDoubleEscape = False
        g.plotLineBackScatter  = False

        g.spectroGammaSelection = []
        for gi in GammaList.selectedItems():
            gitext = (gi.text()).split(":")[0].strip()
            if gitext == "Compton Edge":
                g.plotLineComptonEdge  = True
                continue

            elif gitext == "Single Escape":
                g.plotLineSingleEscape = True
                continue

            elif gitext == "Double Escape":
                g.plotLineDoubleEscape = True
                continue

            elif gitext == "Back Scatter":
                g.plotLineBackScatter  = True
                continue

            else:
                g.spectroGammaSelection.append(gitext)

        updateEditBoxes()
        fillEnergyBoxes()
        plotGraphSpectro()

        # irdprint(defname, f"g.spectroGammaSelection: {g.spectroGammaSelection}")

    updateEditBoxes()
    fillEnergyBoxes()
    plotGraphSpectro()


def printGammaLines():
    """Print to NotePad all isotopes with their energies and list sorted by energies"""

    defname = "printGammaLines: "

    sprint(headerSpec("Gamma Lines [keV]"))

    sprint("Sorted by Sourc")
    sprint("Isotope  : Energy")
    for i, iso in enumerate(g.IsotopeData):
        if iso in ("Compton Edge", "Single Escape", "Double Escape", "Back Scatter"): continue
        isos = ", ".join(f"{ID}" for ID in g.IsotopeData[iso])
        sprint(f"{iso:9s}: {isos}")
    sprint("")


    sprint("Sorted by Energy:")
    sprint("Energy   : Isotope Compton-Edge  SingleEsc  DoubleEsc   BackScat")

    PHlist = []
    for i, iso in enumerate(g.IsotopeData):
        if iso in ("Compton Edge", "Single Escape", "Double Escape", "Back Scatter"): continue
        for isoen in g.IsotopeData[iso]:
            PHlist.append((isoen, iso))
    # ydprint(defname, sorted(PHlist))

    for geng, giso in sorted(PHlist):
        CEgl = getComptonEdge(geng)
        SEgl = geng - 511  if geng >= 1022 else g.NAN
        DEgl = geng - 1022 if geng >= 1022 else g.NAN
        BSgl = geng - CEgl
        sprint(f"{geng:8.3f} : {giso[:10]:10s}  {CEgl:8.3f}   {SEgl:8.3f}   {DEgl:8.3f}   {BSgl:8.3f}")
    sprint("")


def PolynomValue(x, *p):
    """Get Polynomial Function Value for x and paramters p"""

    defname = "PolynomValue: "
    # ydprint(defname, "type(x): ", type(x))

    try:
        if   len(p) == 6:     gvalue = p[0] + p[1] * x + p[2] * x**2 + p[3] * x**3 + p[4] * x**4 + p[5] * x**5
        elif len(p) == 5:     gvalue = p[0] + p[1] * x + p[2] * x**2 + p[3] * x**3 + p[4] * x**4
        elif len(p) == 4:     gvalue = p[0] + p[1] * x + p[2] * x**2 + p[3] * x**3
        elif len(p) == 3:     gvalue = p[0] + p[1] * x + p[2] * x**2
        elif len(p) == 2:     gvalue = p[0] + p[1] * x
        elif len(p) == 1:     gvalue = p[0]
        else:                 gvalue = x

    except Exception as e:
        exceptPrint(e, defname + f"Poly Calculation")
        gvalue = x

    return gvalue


def getFitEnergyCalib(x, verbose=False):
    """return the fit paramters of the energy to channel calibration curve"""

    defname = gd(sys._getframe().f_code.co_name)

    try:
        fitDegree   = 3                                 # fit 3rd order (= 4 paraqmeters)
        fitChnl     = np.array(range(0, len(x)))        # setup channels
        fitEngy     = x                                 # use x-array as energy
        # irdprint(defname, f"fitChnl: {len(fitChnl)}")
        # irdprint(defname, f"fitEngy: {len(fitEngy)}")

        ### make the polynome fit
        try:
            popt = np.polyfit(fitChnl, fitEngy, fitDegree)
            popt = np.flip(popt)                            # flip order to have Offset first, cubic term last

            irdprint(defname, f"popt: {popt} ")             # popt: like:  [1.0, 5.9592, 0, 0] (here linear term only)
            for i, val in enumerate(popt):
                    if abs(val) < 0.0001 / 1E4**i: popt[i] = 0.0
            irdprint(defname, f"popt: {popt} ")             # popt: like:  [1.0, 5.9592, 0, 0] (here linear term only)


            invpopt = np.polyfit(fitEngy, fitChnl, fitDegree)
            invpopt = np.flip(invpopt)                      # flip order to have Offset first, cubic term last
            irdprint(defname, f"invpopt: {invpopt} ")       # inpopt: invers polynom

        except Exception as e:
            exceptPrint(e, f"Fitting Failure")
            popt        = [g.NAN, g.NAN, g.NAN, g.NAN]      # default (if fit fails)

        else:
            if verbose:
                sprint(headerSpec("Fitting the Calibration of Energy vs. Channel"))
                sprint(f"Degree of Fit-Polynom: {fitDegree} - Formula: y = a + b * Ch + c * Ch² + d * Ch³ ")
                sprint("Coefficients:                 a         b         c         d |")
                sprint("Fit Result:           {:+>9.2E} {:+>9.2E} {:+>9.2E} {:+>9.2E} |     Total".format(*popt))

                try:
                    channels = (1, 100, 1000, 10000)
                    for chnl in channels:
                        # if (1 + np.log10(g.spectroDataLen)) >= np.log10(chnl):          # print only lines of same order of mag of channels
                        if 1:
                            a = []
                            for i, pop in enumerate(popt):  a.append(pop * chnl**i)
                            sprint(f"Energy[keV] @Ch={chnl:<5d}:{a[0]:+9.2f} {a[1]:+9.2f} {a[2]:+9.2f}{a[3]:+10.2f} |{sum(a):10.2f}")
                except Exception as e:
                    exceptPrint(e, defname + "printing Fit pops")

                sprint("")

                # inverse popt
                if g.debug:
                    sprint(headerSpec("INVERSE: Fitting the Calibration of Channel vs. Energy"))
                    sprint(f"Degree of Fit-Polynom: {fitDegree} - Formula: y = a + b * En + c * En² + d * En³ ")
                    sprint("Coefficients:                 a         b         c         d |")
                    sprint("Fit Result:           {:+>9.2E} {:+>9.2E} {:+>9.2E} {:+>9.2E} |     Total".format(*invpopt))

                    try:
                        energy = (10, 100, 1000, 10000)
                        for en in energy:
                            if  1 or (1 + np.log10(g.spectroDataLen)) >= np.log10(en):     # print only lines of same order of mag of channels
                                a = []
                                for i, invpop in enumerate(invpopt):  a.append(invpop * en**i)
                                sprint(f"Channel  @En={en:<8.2f}:{a[0]:+9.2f} {a[1]:+9.2f} {a[2]:+9.2f}{a[3]:+10.2f} |{sum(a):10.2f}")
                    except Exception as e:
                        exceptPrint(e, defname + "printing Fit inv-pops")

                    sprint("")


    except Exception as e:
        exceptPrint(e, defname + "overall")


    # irdprint(defname, f"now about to returning popt: {popt} ")
    return popt


def XMLprettyprint(element, **kwargs):
    """PrettyPrint of XML data to Terminal"""

    xml = etree.tostring(element, pretty_print=True, **kwargs)
    print(xml.decode(), end='')


def getFitColor(r2):
    """Choose color for use in Terminal"""

    if   r2 >= 0.9: fitcolor = INVGREEN
    elif r2 >= 0.8: fitcolor = INVORANGE
    else:           fitcolor = INVRED

    return fitcolor


def getFitColorPlot(r2):
    """Choose color for use in Plot"""

    if      r2 >= 0.9: fitcol = "#0f0"     # green     good
    elif    r2 >= 0.8: fitcol = "orange"   # orange    bad
    else:              fitcol = "#f00"     # reddish   ugly

    return fitcol


# reset Clip
def resetClip():
    """reset the clip to show the full spectrum"""

    defname = gd(sys._getframe().f_code.co_name)

    dprint(defname)

    g.spectroLeftClipEnergy  = -10000
    g.spectroRightClipEnergy = +100000

    makeFitPeak()
    g.clipFitCounts = g.NAN
    updateEditBoxes()
    plotGraphSpectro()


# reset Fit
def resetFit():
    """reset the fit to not-fitted state and full width of spectrum"""

    defname = gd(sys._getframe().f_code.co_name)
    dprint(defname)

    g.spectroLeftFitEnergy     = -10000
    g.spectroRightFitEnergy    = +10000
    g.spectroLeftClipCounts    = 0
    g.spectroRightClipCounts   = 0

    if g.spectroLeftFitEnergy  < g.spectroLeftClipEnergy:  g.spectroLeftFitEnergy  = g.spectroLeftClipEnergy
    if g.spectroRightFitEnergy > g.spectroRightClipEnergy: g.spectroRightFitEnergy = g.spectroRightClipEnergy
    if g.checkFit.isChecked(): g.checkFit.setChecked(False)

    makeFitPeak()
    g.clipFitCounts = g.NAN
    updateEditBoxes()
    plotGraphSpectro()


def assenbleSpectraIntoPDF():
    """Search for Spectra files in to be selected dir and all sub dirs and put into a pdf file"""

    #######################################################################################################

    def find_all(ext, path):
        """find all matches with extension ext in path"""

        fnames = []
        for root, dirs, files in os.walk(path):
            # cdprint(defname, f"dirs: {dirs}  files: {files}")
            for fname in files:
                if fname.endswith(ext):
                    # cdprint(defname, f"dirs: {dirs}  file: {fname}")
                    fnames.append([ext, fname, root])
                    # gdprint(defname, f"ext: {ext:>8s}  filecounter: {filecounter:3d}:  {fname}   root: {root}")

        return fnames


    def selectDir():
        """Allow selection from a dialog"""

        oldStartDir = startdir.text().strip()
        newStartDir = QFileDialog.getExistingDirectory(None, "Select Start Directory for Spectra Scan", newDir, \
                                                       QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks)
        irdprint(defname, f"New StartDir: {newStartDir}")
        if newStartDir > "":   startdir.setText(newStartDir)
        else:                  startdir.setText(oldStartDir)


    #######################################################################################################

    # defname = "assenbleSpectraIntoPDF: "
    defname = gd(sys._getframe().f_code.co_name)

    dprint(defname)
    setIndent(1)

    fprint(header("Assembling Spectra Files into PDF"))
    QtUpdate()

    # new dir => working dir + data dir
    newDir = os.path.join(os.getcwd(), "data")
    cdprint(defname, f"Default directory for search: {newDir}")

    pdffileName = "0000_Spectra_Collection.pdf"

    startdir = QLineEdit()
    startdir.setToolTip("Edit or Select the directory in which to start the scan")
    startdir.setMinimumWidth(450)
    startdir.setText(newDir)

    dirselect = QPushButton("Select different directory")
    dirselect.setAutoDefault(False)
    dirselect.setToolTip("Push button to open a directory-select dialog")
    dirselect.clicked.connect(lambda:  selectDir())

    pdfName = QLineEdit()
    pdfName.setToolTip("Set the depth: (set 0 to scan all)")
    pdfName.setText(pdffileName)

    cutChannels = QLineEdit()
    cutChannels.setToolTip("Set the percentage of channels to cut-off from the end")
    cutChannels.setText(f"{3.0:0.3g}")

    bbox = QDialogButtonBox()
    bbox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok )
    bbox.accepted.connect(lambda: dlg.done(100))
    bbox.rejected.connect(lambda: dlg.done(0))

    fbox = QFormLayout()
    fbox.setFieldGrowthPolicy (QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
    fbox.addRow(QLabel("Start Directory of the Scan:"), startdir)
    fbox.addRow(QLabel(""),                             dirselect)
    fbox.addRow(QLabel("Name of PDF file:"),            pdfName)
    fbox.addRow(QLabel("Percent of channels to cut-off  \nfrom the end: [%]"), cutChannels)

    layoutV = QVBoxLayout()
    layoutV.addLayout(fbox)
    layoutV.addWidget(bbox)

    dlg = QDialog() # set parent to None to popup in center of screen
    dlg.setWindowIcon(g.iconGeigerLog)
    dlg.setFont(g.fontstd)
    dlg.setWindowTitle("Assemble Spectra Files into PDF Album")
    dlg.setWindowModality(Qt.WindowModality.NonModal)
    dlg.setLayout(layoutV)

    retval = dlg.exec()
    # print("retval:", retval)

    if retval == 0:
        msg = "PDF creation cancelled"
        fprint(msg)
        dprint(defname, msg)
        setIndent(0)
        return

    elif retval == 100:
        StartDir = startdir.text().strip()
        irdprint(defname, f"Current StartDir: {StartDir}  ")

        pdffileName  = pdfName.text().strip()
        irdprint(defname, f"PDF Filenam     {pdffileName}  ")

        try:    cutoffChannels = float(cutChannels.text().strip())
        except: cutoffChannels = 0.0
        irdprint(defname, f"Spectrum cutoff:  {cutoffChannels}  ")

    # File type for extensions to search for
    FileType = {"xml"        : "XML-RadiaCode",
                "SPE.csv"    : "CSV-GEN",
                "MC.csv"     : "CSV-MC",
                "spe"        : "HDS101-CSV-SPE",
                "CNF"        : "CANBERRA-CNF",
                "TKA"        : "CANBERRA-TKA",
                "n42"        : "XML-N42",
               }

    pagecounter, xcounter, ycounter = 0, 0, 0

    # Create instance of FPDF class
    pdf = FPDF()
    pdf.set_font("Arial", size = 12)            # Set font

    filecounter = 1
    for ext in FileType:
        result = find_all(ext, StartDir)
        # irdprint(defname, f"---------------------len(result):  {len(result)}  {result[0:10]}")

        datadir   = getPathToDataDir()
        outputdir = os.path.join(datadir, "spectraplots")
        if not os.path.exists(outputdir): os.makedirs(outputdir)

        if len(result) == 0:
            continue
        else:
            xcounter  = 0
            ycounter  = 0
            pdf.add_page()
            pagecounter += 1
            pdf.cell(200, 10, txt = "GeigerLog Spectra Collection", ln = True, align = 'C', border=0)
            pdf.cell(200, 10, txt = f"Pag {pagecounter}  File Typ {ext}", ln = True, align = 'C', border=0)

        for i, rslt in enumerate(result):
            # ### testing
            # if filecounter > 27: break
            # ###

            ext, fname, root = rslt                                         # extension to search for, Filename, path to filename

            msg = f"#{filecounter:>4d}-{i + 1:<4d} {ext:<7s}  {fname:42s}  {root}"
            dprint(defname, msg)
            fprint(msg)
            QtUpdate()

            source      = FileType[ext]
            path        = os.path.join(root, fname)       # full path
            shortpath   = path[len(datadir) - 4 : ]       # includes 'data' in path
            getFileSpectro(defaultSpectroDBPath=path, source=source, restart=False, quiet=True)

            makeGraphs = True
            if makeGraphs:        # on True make graphs
                # create the matplotlib graph
                fig1 = plt.figure(88, figsize=(6, 4), facecolor="#f9f9f1")
                fig1.clf()
                rax1 = fig1.add_subplot()
                plt.subplots_adjust(hspace=None, wspace=.2 , left=.15, top=0.9, bottom=0.11, right=.98)
                rax1.set_xlabel(u'Energy or Channel')
                rax1.set_ylabel(u'Counts')
                rax1.set_title(shortpath, fontsize=9, loc='right')

                # plot the spectrum
                chan   = g.spectroData[:, 0]
                data   = g.spectroData[:, 1]

                # cutoff data from the end, as they may distort the whole spectrum by being very high
                cutlen = int(len(chan) * cutoffChannels / 100.0)
                irdprint(defname, f"cutlen: {cutlen}")
                if cutlen == 0: rax1.plot(chan,           data,           'b-', lw=1.0)
                else:           rax1.plot(chan[:-cutlen], data[:-cutlen], 'b-', lw=1.0)

                # show and save
                fig1.show()
                if "WINDOWS" in platform.platform().upper():    fname = shortpath.replace("\\", "_")
                else:                                           fname = shortpath.replace("/" , "_")
                outputfname = os.path.join(outputdir, f"{fname}.png")
                fig1.savefig(outputfname)
                plt.close(88)

            else:
                # Don't make any graphs (for testing; must copy the "test_ag108.n42.png" file!)
                outputfname = os.path.join(outputdir, "test_ag108.n42.png")

            # Add an image to the pdf and increment position counters
            irdprint(defname, f"outputfname: {outputfname}")
            pdf.image(outputfname, x = 20 + 91 * xcounter, y = 30 + 51 * ycounter, w = 90, h = 50)
            xcounter += 1
            if xcounter == 2:
                ycounter += 1
                xcounter  = 0
                if ycounter == 5:
                    ycounter = 0
                    xcounter = 0
                    pdf.add_page()
                    pagecounter += 1
                    pdf.cell(200, 10, txt = "GeigerLog Spectra Collection", ln = True, align = 'C', border=0)
                    pdf.cell(200, 10, txt = f"Pag {pagecounter}  File Typ {ext}", ln = True, align = 'C', border=0)

            filecounter += 1

    # Save the finished PDF to a file
    pdffilepath = os.path.join(outputdir, pdffileName)
    pdf.output(pdffilepath)

    fprint(f"PDF with Spectra Images created successfully on Filepath:\n{pdffilepath}")
    fprint("")
    setIndent(0)


def fillCalibFormula():
    OffScale.setText(f"{g.spectroScale[0]:0.7g}")
    LinScale.setText(f"{g.spectroScale[1]:0.7g}")
    SqrScale.setText(f"{g.spectroScale[2]:0.7g}")
    CubScale.setText(f"{g.spectroScale[3]:0.7g}")


def moduleCalibFormula(dlg=None):
    """make the Layout for the 4-Parameter Calibration"""

    global OffScale, LinScale, SqrScale, CubScale

    defname = "moduleCalibFormula: "
    # irdprint(defname)

    CalibHeader = QLabel(f"Calibration Fitting Result")
    CalibHeader.setFont(g.fontstd)
    CalibHeader.setStyleSheet("font-weight: 1000;")

    CalibNote = QLabel(f"Energy [keV] = a + b*Chnl + c*Chnl² + d*Chnl³")
    CalibNote.setFont(g.fontstd)

    maxChannel = g.spectroDataLen - 1

    ImpactLabel = QLabel("Impact (❓)")
    ImpactLabel.setToolTip(f"The contribution of this term to the Gamma Energy [keV] at MaxChannel={maxChannel}")

    # Offset
    def setOffImpact():
        val = getFloat(OffScale.text())
        OffImpact.setText((f"{val:>7,.0f}"))
        if dlg is not None: dlg.done(111)

    OffLabel = QLabel("a - Offset")
    OffScale = QLineEdit()
    OffScale.setToolTip("Enter a value to offset Energy\n'-' : Curve shifts left; '+' : Curve shifts right")
    OffScale.setText(f"{g.spectroScale[0]:0.7g}")
    OffScale.textChanged     .connect(lambda:  setOffImpact())
    OffScale.setValidator(QDoubleValidator(g.MINF, g.PINF, 20))
    OffScale.setReadOnly(True)
    OffScale.setStyleSheet("background-color:#EEEEEC;")
    OffImpact = QLabel(f"{g.spectroScale[0]:>7,.0f}")
    OffImpact.setAlignment(Qt.AlignmentFlag.AlignRight)

    # Linear
    def setLinImpact():
        val = getFloat(LinScale.text())
        LinImpact.setText((f"{val * maxChannel:>7,.0f}"))
        if dlg is not None: dlg.done(111)

    LinLabel = QLabel("b - Linear")
    LinScale = QLineEdit()
    LinScale.setToolTip("Enter a value to scale Energy\n'<1' : Curve shifts left; '>1' : Curve shifts right")
    LinScale.setText(f"{g.spectroScale[1]:0.7g}")
    LinScale.textChanged     .connect(lambda:  setLinImpact())
    LinScale.setValidator(QDoubleValidator(g.MINF, g.PINF, 20))
    LinScale.setReadOnly(True)
    LinScale.setStyleSheet("background-color:#EEEEEC;")
    LinImpact = QLabel(f"{g.spectroScale[1] * maxChannel:>7,.0f}")
    LinImpact.setAlignment(Qt.AlignmentFlag.AlignRight)


    # Square
    def setSqrImpact():
        val = getFloat(SqrScale.text())
        SqrImpact.setText((f"{val * maxChannel**2:>7,.0f}"))
        if dlg is not None: dlg.done(111)

    SqrLabel = QLabel("c - Quadratic")
    SqrScale = QLineEdit()
    SqrScale.setToolTip("Enter a value to scale Energy")
    SqrScale.setText(f"{g.spectroScale[2]:0.9g}")
    SqrScale.textChanged     .connect(lambda:  setSqrImpact())
    SqrScale.setValidator(QDoubleValidator(g.MINF, g.PINF, 20))
    SqrScale.setReadOnly(True)
    SqrScale.setStyleSheet("background-color:#EEEEEC;")
    SqrImpact = QLabel(f"{g.spectroScale[2] * maxChannel**2:>7,.0f}")
    SqrImpact.setAlignment(Qt.AlignmentFlag.AlignRight)

    # Cubic
    def setCubImpact():
        val = getFloat(CubScale.text())
        CubImpact.setText((f"{val * maxChannel**3:>7,.0f}"))
        if dlg is not None: dlg.done(111)

    CubLabel = QLabel("d - Cubic")
    CubScale = QLineEdit()
    CubScale.setToolTip("Enter a value to scale Energy")
    CubScale.setText(f"{g.spectroScale[3]:0.9g}")
    CubScale.textChanged     .connect(lambda:  setCubImpact())
    CubScale.setValidator(QDoubleValidator(g.MINF, g.PINF, 20))
    CubScale.setReadOnly(True)
    CubScale.setStyleSheet("background-color:#EEEEEC;")
    CubImpact = QLabel(f"{g.spectroScale[3] * maxChannel**3:>7,.0f}")
    CubImpact.setAlignment(Qt.AlignmentFlag.AlignRight)

    scaleBox=QGridLayout()
    scaleBox.setContentsMargins(0,5,15,5) # spacing around the table

    row = 0
    scaleBox.addWidget(QLabel("Values of Parameters"),      row, 1, 1, 2)
    scaleBox.addWidget(ImpactLabel,                         row, 3)

    row += 1
    scaleBox.addWidget(OffLabel,                            row, 1)
    scaleBox.addWidget(OffScale,                            row, 2)
    scaleBox.addWidget(OffImpact,                           row, 3)

    row += 1
    scaleBox.addWidget(LinLabel,                            row, 1)
    scaleBox.addWidget(LinScale,                            row, 2)
    scaleBox.addWidget(LinImpact,                           row, 3)

    row += 1
    scaleBox.addWidget(SqrLabel,                            row, 1)
    scaleBox.addWidget(SqrScale,                            row, 2)
    scaleBox.addWidget(SqrImpact,                           row, 3)

    row += 1
    scaleBox.addWidget(CubLabel,                            row, 1)
    scaleBox.addWidget(CubScale,                            row, 2)
    scaleBox.addWidget(CubImpact,                           row, 3)


    layoutV = QVBoxLayout()
    # layoutV.addWidget(QLabel(""))
    layoutV.addWidget(CalibHeader)
    layoutV.addWidget(CalibNote)
    layoutV.addLayout(scaleBox)

    return layoutV


##############################################################################################################################
##############################################################################################################################
##############################################################################################################################
##############################################################################################################################
##############################################################################################################################
##############################################################################################################################
##############################################################################################################################

#calib
def Calibration():
    """Calib by fitting to peaks"""

    global cax1, cax2, CalibPosition, FitdegreeButton

    defname = gd(sys._getframe().f_code.co_name)
    # dprint(defname)

    setIndent(1)

    g.calibLeft             = [0,                   None]        # the left edge of the spectrum in channel numbers
    g.calibRight            = [len(g.Counts) - 1,   None]        # the right edge of the spectrum in channel numbers
    g.calibLeftFit          = [None,                None]        # the left edge of the spectrum to be fitted in channel numbers
    g.calibRightFit         = [None,                None]        # the right edge of the spectrum to be fitted in channel numbers

    while True:                    # break only on OK and Cancel
        if len(g.CalPeak) == 0:
            maxCalibPairs = len(g.spectroCalibLines)

            # add the headers in row 0
            g.CalPeak.append([QLabel(), QLabel(), QLabel(), QLabel()])
            g.CalPeak[0][0].setText("Indx")
            g.CalPeak[0][1].setText("Channel")
            g.CalPeak[0][2].setText("Energy")
            g.CalPeak[0][3].setText("Comment")

            def addFitMean():
                # irdprint(f"addFitMean")
                for i in range(0, maxCalibPairs):
                    if g.CalPeak[i + 1][0].hasFocus():
                        # irdprint(f"addFitMean hasFocus at i: {i}")
                        g.CalPeak[i + 1][1].setText(g.calibMeanGauss.text().strip())
                        break

            # add the fields on the other rows
            for i in range(1, maxCalibPairs + 1):
                if i == 1: g.CalPeak.append([QPushButton(), QLineEdit(), QLineEdit(), QLabel()])
                else:      g.CalPeak.append([QPushButton(), QLineEdit(), QLabel(), QLabel()])

                g.CalPeak[i][0].setFixedWidth(30)
                g.CalPeak[i][1].setFixedWidth(75)
                g.CalPeak[i][2].setFixedWidth(70)

                g.CalPeak[i][3].setTextInteractionFlags(Qt.TextInteractionFlag(1))

                # g.CalPeak[i][1].returnPressed.connect(lambda:  addFitMean())                     # allow all indx to set channel


            for i in range(0, maxCalibPairs):
                channel, energy, comment = g.spectroCalibLines[i].split(",", 2)
                # irdprint(defname, f"{channel}, {energy}, {comment}: {g.spectroCalibLines[i]}")

                g.CalPeak[i + 1][0].setText(f" #{i + 1} ")                      # into Label (index)
                g.CalPeak[i + 1][0].clicked.connect(lambda:  addFitMean())
                g.CalPeak[i + 1][1].setText(channel)                            # into LineEdit (channel number as float)
                g.CalPeak[i + 1][2].setText(energy)                             # into Label (isotope energy)
                g.CalPeak[i + 1][3].setText(comment)                            # into Label (Isotope name)
                tooltip = "Other energies: "
                try:
                    cmts = comment.split(",")
                    for cmt in cmts:
                        tooltip += str(g.IsotopeData[cmt.strip()]) + "  "
                except Exception as e:
                    tooltip += "N.A."

                g.CalPeak[i + 1][3].setToolTip(tooltip)

        PeakTable=QGridLayout()
        PeakTable.setContentsMargins(5,5,5,5) # spacing around the table
        for row in range(0, len(g.CalPeak)):
            PeakTable.addWidget(g.CalPeak[row][0],   row, 0)
            PeakTable.addWidget(g.CalPeak[row][1],   row, 1)
            PeakTable.addWidget(g.CalPeak[row][2],   row, 2)
            PeakTable.addWidget(g.CalPeak[row][3],   row, 3)

        # Fit degree
        FitdegreeButton = QComboBox()       # "Fit Degree"
        FitdegreeButton.addItems(["Linear", "Quadratic", "Cubic"])
        FitdegreeButton.setToolTip("Select the maximum degree your Polynome fit should have")
        FitdegreeButton.setCurrentIndex(2)
        FitdegreeButton.currentIndex()

        # Apply button
        applyButton = QPushButton("Apply Calibration")
        applyButton.setAutoDefault(False)                      # do NOT react to Enter key!
        applyButton.clicked.connect(lambda: fitCalib())
        applyButton.setFixedWidth(150)


        def execOK():
            # success = fitCalib()
            # if success:  dlg.done(100)
            dlg.done(100)

        # OK button
        okButton = QPushButton("OK")
        okButton.setAutoDefault(False)                      # do NOT react to Enter key!
        # okButton.clicked.connect(lambda: dlg.done(100))
        okButton.clicked.connect(lambda: execOK())

        # OK & Save to database
        SaveCalibButton = QPushButton("OK && Save")
        SaveCalibButton.setAutoDefault(False)
        SaveCalibButton.setToolTip("Use entries as new calibration and update database")
        SaveCalibButton.clicked.connect(lambda:  dlg.done(105))

        # Cancel button
        cancelButton = QPushButton("Cancel")
        cancelButton.setAutoDefault(False)
        cancelButton.clicked.connect(lambda: dlg.done(0))

        # Help button
        helpButton = QPushButton("Help")
        helpButton.setAutoDefault(False)
        helpButton.clicked.connect (lambda: showHelpMsg())

        # Reset button
        resetButton = QPushButton("Reset")
        resetButton.setAutoDefault(False)
        resetButton.clicked.connect(lambda: dlg.done(101))

        # Save Button
        SaveCalibGraphButton = QPushButton("Save Graph")
        SaveCalibGraphButton.setAutoDefault(False)
        SaveCalibGraphButton.setToolTip("Save current graph as png-file")
        SaveCalibGraphButton.clicked.connect(lambda:  saveCalibGraph())

        # reset Graph and Fit
        def resetGraph():

            # g.redMarker.setText(f"")
            g.calibMeanGauss.setText(f"")

            g.calibFitResult    = None
            g.calibLeft         = [0,                   None]
            g.calibRight        = [len(g.Counts) - 1,   None]
            g.calibLeftFit      = [0,                   None]
            g.calibRightFit     = [len(g.Counts) - 1,   None]

            channels = range(0, len(g.Counts))
            counts   = g.Counts.copy()
            plotGraphCalib(channels, counts)

        resetCalibGraphButton = QPushButton("Reset Graph")
        resetCalibGraphButton.setAutoDefault(False)
        resetCalibGraphButton.setToolTip("Reset the Fit paramters")
        resetCalibGraphButton.clicked.connect(lambda:  resetGraph())

        bbox = QDialogButtonBox()
        bbox.addButton(helpButton,              QDialogButtonBox.ButtonRole.HelpRole)
        bbox.addButton(SaveCalibGraphButton,    QDialogButtonBox.ButtonRole.HelpRole)
        bbox.addButton(resetCalibGraphButton,   QDialogButtonBox.ButtonRole.HelpRole)
        bbox.addButton(resetButton,             QDialogButtonBox.ButtonRole.ActionRole)
        bbox.addButton(SaveCalibButton,         QDialogButtonBox.ButtonRole.ActionRole)
        bbox.addButton(cancelButton,            QDialogButtonBox.ButtonRole.ActionRole)
        bbox.addButton(okButton,                QDialogButtonBox.ButtonRole.ActionRole)

        CalibPosition = QLineEdit()
        # CalibPosition.setText("Cursor Position")
        CalibPosition.setText("Mouse Position on Graph")
        CalibPosition.setReadOnly(True)
        CalibPosition.setFixedWidth(260)
        CalibPosition.setStyleSheet("background-color:#EEEEEC;")
        CalibPosition.setAlignment(Qt.AlignmentFlag.AlignHCenter)


        # Gauss fit mean
        g.calibMeanGauss = QLineEdit()
        # g.calibMeanGauss.setDragEnabled(True)
        # g.calibMeanGauss.setToolTip("For change press Cursor (Alt-)left/right; For reset press Reset")
        g.calibMeanGauss.setReadOnly(True)
        g.calibMeanGauss.setStyleSheet("background-color: #00ff00; font-weight:bold;")
        # g.calibMeanGauss.setMaximumWidth(70)
        g.calibMeanGauss.setMaximumWidth(70)

        # # red marker
        # g.redMarker = QLineEdit()
        # g.redMarker.setDragEnabled(True)
        # g.redMarker.setToolTip("For change press Cursor (Alt-)left/right; For reset press Reset")
        # g.redMarker.setReadOnly(False)
        # g.redMarker.setValidator(QDoubleValidator(-10000, +10000, 2))
        # g.redMarker.setStyleSheet("background-color: #f00; color:white; font-weight:bold;")
        # g.redMarker.setMaximumWidth(70)

        # # make markerline layout
        # markerLine = QHBoxLayout()
        # # markerLine.addWidget(QLabel("Red Marker:"))
        # # markerLine.addWidget(g.redMarker)
        # # markerLine.addStretch()
        # markerLine.addWidget(QLabel("Gauss Fit Mean:"))
        # markerLine.addWidget(g.calibMeanGauss)
        # markerLine.addStretch()

        peakBox = QWidget()
        peakBox.setLayout(PeakTable)

        scrollArea = QScrollArea()
        scrollArea.setWidget(peakBox)

        buttonLine = QHBoxLayout()
        buttonLine.addWidget(QLabel("Max Fit Degree:"))
        buttonLine.addWidget(FitdegreeButton)
        buttonLine.addStretch()
        buttonLine.addWidget(applyButton)

        # right layout
        layoutCalV1 = QVBoxLayout()
        # layoutCalV1.addLayout(markerLine)
        layoutCalV1.addWidget(scrollArea)
        layoutCalV1.addLayout(buttonLine)
        layoutCalV1.addLayout(moduleCalibFormula())

        dlg = QDialog()
        dlg.setWindowIcon(g.iconGeigerLog)
        dlg.setFont(g.fontstd)
        dlg.setWindowTitle(f"Calibration: '{g.spectroDBPath}'")
        # dlg.setWindowModality(Qt.WindowModality.NonModal)
        dlg.setWindowModality(Qt.WindowModality.WindowModal)
        dlg.setMinimumHeight(750)

        # make figure
        CalibFigureNo = 999
        plt.close(CalibFigureNo)
        g.figCalib = plt.figure(CalibFigureNo, figsize=(8, 5.5), facecolor="#C9F9F0", dpi=g.hidpiScaleMPL, clear=True) # facecolor="#C9F9F0": blueish tint
        plt.subplots_adjust(hspace=None, wspace=None , left=.12, top=0.95, bottom=0.1, right=.9)

        # make canvas
        def setCalibCanvasFocus(event):
            """Canvas gets focus when mouse hovers over the figure"""
            defname = gd(sys._getframe().f_code.co_name)
            g.canvasCalib.setFocus()


        def removeCalibCanvasFocus(event):
            """okButton gets focus when mouse LEAVES the figure"""
            defname = gd(sys._getframe().f_code.co_name)
            okButton.setFocus()


        def updateCalibCursorPos(event):
            """when cursor inside plot, get position and print to status field"""

            defname = gd(sys._getframe().f_code.co_name)

            try: # results in non-breaking error messages when no data are displayed
                if event.inaxes:
                    # irdprint(f"{event}")
                    x  = event.x
                    y  = event.y
                    xd = event.xdata
                    yd = event.ydata
                    # if yd < 1.0 : yd=g.NAN

                    ydata = event.ydata
                    ylBot, ylTop = cax1.get_ylim()
                    yrBot, yrTop = cax2.get_ylim()
                    yleft = (ydata - yrBot) / (yrTop - yrBot) * (ylTop - ylBot) + ylBot
                    # rdprint(defname, f"updatecursorposition: x:{x:0.10f} y1:{y1:0.3f}  y2:{y2:0.3f}")

                    ch = customformat(xd,       5, 1, thousand=False)
                    cn = customformat(yleft,    5, 1, thousand=False)
                    wd = customformat(yd,       5, 1, thousand=False)
                    CalibPosition.setText(f" Chnl:{ch} Cnts:{cn} Wdth:{wd}")
                else:
                    # CalibPosition.setText("Cursor Position")
                    CalibPosition.setText("Mouse Position on Graph")

            except Exception as e:
                exceptPrint(e, defname)


        g.canvasCalib = FigureCanvas(g.figCalib)
        g.canvasCalib.mpl_connect('button_press_event',  onCalibMouseClick)           # send a mouse button click event
        g.canvasCalib.mpl_connect('key_press_event',     onCalibKeyPress)           # sent when the mouse cursor enters the figure
        g.canvasCalib.mpl_connect('figure_enter_event',  setCalibCanvasFocus)    # sent when the mouse cursor enters the figure
        g.canvasCalib.mpl_connect('figure_leave_event',  removeCalibCanvasFocus) # sent when the mouse cursor EXITS the figure
        g.canvasCalib.mpl_connect('motion_notify_event', updateCalibCursorPos)   # send a mouse button click event

        # Check Calib Show Grid
        def toggleShowGrid():
            g.calibShowGrid = checkCalibShowGrid.isChecked()
            plotGraphCalib()

        checkCalibShowGrid = QCheckBox("Grid")
        checkCalibShowGrid.setChecked(g.calibShowGrid)
        checkCalibShowGrid.setToolTip("Show the Grid in the Graph")
        checkCalibShowGrid.stateChanged.connect(lambda:  toggleShowGrid())


        # Check Calib Show Log
        def toggleShowLog():
            g.calibShowLog = checkCalibShowLog.isChecked()
            plotGraphCalib()

        checkCalibShowLog = QCheckBox("Log")
        checkCalibShowLog.setChecked(g.calibShowLog)
        checkCalibShowLog.setToolTip("Show the Log 0f Spectr in the Graph")
        checkCalibShowLog.stateChanged.connect(lambda:  toggleShowLog())


        # Check Calib Show Lines
        def toggleShowLine():
            g.calibShowLine = checkCalibShowLine.isChecked()
            plotGraphCalib()

        checkCalibShowLine = QCheckBox("Lines")
        checkCalibShowLine.setChecked(g.spectroShowLine)
        checkCalibShowLine.setToolTip("Show connecting lines between dots")
        checkCalibShowLine.stateChanged.connect(lambda:  toggleShowLine())


        # Check Show Energy & Channel Width
        def toggleShowEW():
            g.calibShowEW = checkCalibShowEW.isChecked()
            plotGraphCalib()

        checkCalibShowEW = QCheckBox("E&&W")
        checkCalibShowEW.setChecked(g.calibShowEW)
        checkCalibShowEW.setToolTip("Add the Energy and Channel Width curves")
        checkCalibShowEW.stateChanged.connect(lambda:  toggleShowEW())


        # Check Calib Show Orig E + W
        def toggleOrig():
            g.calibShowOrig = not g.calibShowOrig
            plotGraphCalib()

        # Orig button
        checkCalibShowOrig = QCheckBox("E&&W-Orig")
        checkCalibShowOrig.setToolTip("Toggle Show / Not Show original Energy and Channel width data")
        checkCalibShowOrig.clicked.connect  (lambda: toggleOrig())

        # my Stretch
        CustomStretch = QWidget()
        CustomStretch.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        ### Toolbar
        calibToolbar = QToolBar("Calib Toolbar")
        calibToolbar.addWidget(checkCalibShowEW)
        calibToolbar.addWidget(checkCalibShowOrig)
        calibToolbar.addWidget(CustomStretch)
        calibToolbar.addWidget(checkCalibShowGrid)
        calibToolbar.addWidget(checkCalibShowLine)
        calibToolbar.addWidget(checkCalibShowLog)
        calibToolbar.addWidget(CalibPosition)
        # calibToolbar.addLayout(markerLine)
        calibToolbar.addWidget(QLabel("  Gauss Fit Mean: "))
        calibToolbar.addWidget(g.calibMeanGauss)


        # left layout
        layoutCalV2 = QVBoxLayout()
        layoutCalV2.addWidget(calibToolbar)
        layoutCalV2.addWidget(g.canvasCalib, stretch=1000)   #layoutVR.addWidget(g.canvasSpectro, stretch=1000)

        # both layouts
        layoutCalH = QHBoxLayout()
        layoutCalH.addLayout(layoutCalV2, stretch=1000)
        layoutCalH.addLayout(layoutCalV1)

        # layout full width
        layoutFullV = QVBoxLayout(dlg)                  # linked with dlg
        layoutFullV.addLayout(layoutCalH)
        layoutFullV.addWidget(bbox)

        dlg.setLayout(layoutFullV)

        # plot the counts curve (with marker if defined)
        # if g.redMarkerOld > "": g.redMarker.setText(g.redMarkerOld)
        plotGraphCalib(range(0, len(g.Counts)), g.Counts)

        retval = dlg.exec()
        # print("retval:", retval)
        #calib==========================================================================================================

        success = False
        if retval == 0:
            # cancel (button or ESC; --> exit without any action)
            break

        elif retval == 101:
            # Reset
            resetCalib()

        else:
            # retval == 100 (OK) or ==105 (OK&Save) or ==111 (recalc)
            # values accepted; now make calibration

            sprint(headerSpec("Calibration"))
            # irdprint(defname, f"before fitCalib: {g.spectroScale}")
            success = fitCalib()
            # irdprint(defname, f"after fitCalib: {g.spectroScale}   success: {success}")
            if success:
                # sprint(headerSpec("Calibration"))
                # irdprint(defname, f"next: printSpectroInfo")
                printSpectroInfo()
                # irdprint(defname, f"done: printSpectroInfo")

                # OK & Save     # saving to database when button "OK&Save" clicked
                if retval == 105:
                    appendComments([f"{'GeigerLog Calibration'}::[{', '.join(f'{sS:0.9g}' for sS in g.spectroScale)}]"])
                    msg = "Saved to Database"
                    sprint(msg)
                    dprint(defname, msg)
                    initSpectroGraph(reset=True, overwrite=True)           # re-plot Spectro without resetting

                sprint("")
                resetClip()
                updateEditBoxes()
                plotGraphSpectro()
                plotGraphCalib()

                if retval == 111:   pass            # recalc (do NOT break)
                else:               break
            else:
                sprint("Calibration failed")
                sprint("")

    setIndent(0)

    g.calibShowLog = False      # Log Scale off
    # initSpectroGraph(reset=True, overwrite=True)           # re-plot Spectro without resetting


def fitCalib():
    """applies Polynome fit to isotopes selected for calibration"""

    global FitdegreeButton

    defname = "fitCalib: "

    CalChannel  = []
    CalEnergy   = []
    CalIsotopes = g.CalPeak.copy()

    for i in range(1, len(CalIsotopes)):
        if CalIsotopes[i][1].text().strip() > "":
            try:
                CalChannel.append(float(CalIsotopes[i][1].text().replace(",", ".")))
                CalEnergy .append(float(CalIsotopes[i][2].text().replace(",", ".")))
            except Exception as e:
                exceptPrint(e, "make floats")
                sprint(f"Illegal Data Pair: '{CalIsotopes[i][1].text()} : {CalIsotopes[i][2].text()}' ignoring it")

    # at least 2 energies must be defined
    success = False
    # if len(CalChannel) >= 2:
    if len(CalChannel) > 0:
        irdprint(defname, f"lenCh: {len(CalChannel)}   lenEn: {len(CalEnergy)}   ")

        if len(CalChannel) == 1:
            ### need a second channel
            irdprint(defname, f"Only 1 channel defined; adding 2nd channel as Ch:0, Energy:0")
            CalChannel.append(0.0)
            CalEnergy.append(0.0)

        sprint("Using these data pairs for calibration:")
        sprint("Index Channel     Energy")
        for i in range(len(CalChannel)):
            sprint(f"{i:2d}: {CalChannel[i]:9.3f}  {CalEnergy[i]:9.3f}")

        ### make the polynome fit
        try:
            fitdegree   = min(FitdegreeButton.currentIndex() + 1, len(CalChannel) - 1)
            popt        = np.polyfit(CalChannel, CalEnergy, fitdegree)
            popt        = np.flip(popt)                                     # flip order to have Offset first, cubic term last
            oldpopt     = popt.copy()
            popt[0]     = round(popt[0], 3)
            for i in range(fitdegree + 1, 4): popt = np.append(popt, 0.0)   # append 0 until a total of 4 parameters
            # irdprint(defname, f"fitdegree: {fitdegree} old-popt: {oldpopt}  --> new-popt: {popt}")

        except RuntimeError as e:
            exceptPrint(e, f"Fail Runtime")

        except Exception as e:
            exceptPrint(e, f"Fitting Failure")

        else:
            g.spectroScale = popt
            g.spectroScale[0] = round(g.spectroScale[0], 3)
            msg = ", ".join(f"{p:0.9g}" for p in g.spectroScale)
            sprint(f"Calibration Coefficients: [{msg}]")
            sprint(f"")

            # set to new coeffs
            for i in range(g.spectroDataLen):       g.EnergyCalib[i]       = calibChannelToEnergy(i)
            for i in range(g.spectroDataLen - 1):   g.ChnlWidthCalib[i]    = g.EnergyCalib[i + 1] - g.EnergyCalib[i]

            fillCalibFormula()
            plotGraphCalib()

            success = True

    else:
        # no energies defined - exit without any action
        showMessageBox()

    # irdprint(defname, f"g.spectroScale: {g.spectroScale}") ### g.spectroScale = popt

    return success


def showMessageBox():
    """Error Msg - not enough channels"""

    burp()

    msgtext  = "Can't do Calibration - need settings for at least 1 channel!\n\n"
    msgtext += "If only 1 channel is set, a 2nd one will be used as Channel=0, Energy=0.\n"
    msg = QMessageBox()
    msg.setWindowIcon(g.iconGeigerLog)
    msg.setIcon(QMessageBox.Icon.Warning)
    msg.setWindowTitle("Apply Calibration")
    msg.setText(msgtext)
    msg.setStandardButtons(QMessageBox.StandardButton.Ok )
    msg.exec()


def getMarkerValue():
    """Read the Marker-Value and convert to float"""

    # try:    line = float(g.redMarker.text())
    # except: line = g.NAN

    line = g.NAN

    return line


def resetCalib():
    # g.redMarker.setText(f"")
    g.calibMeanGauss.setText(f"")
    g.CalPeak           = []
    # g.redMarkerOld      = ""
    g.calibShowLog      = False
    g.calibShowOrig     = False
    g.calibShowEW       = False
    g.calibShowLine     = True
    g.calibShowGrid     = True

    g.calibFitResult    = None

    g.calibLeft         = [None, None]
    g.calibRight        = [None, None]
    g.calibLeftFit      = [None, None]
    g.calibRightFit     = [None, None]


def showHelpMsg():

    helptxt = ("""
               - Clip-out desired segment of the spectrum with Control-Left and Control-Right mouse clicks.
                    - Select between Log and Lin plot
                    - Select between drawing connecting lines or dots-only
                    - Select to show a grid or not

               - Do a Middle mouse click roughly on the center of the peak you want to use for calibration
                    - a vertical Red Marker line will be set where you clicked
                    - a peak will be fitted with a Gauss curve and peak area marked in green (good fit),
                      yellow (not good, but perhaps OK), or red (poor fit).
                    - their values will be shown in the red, or green, resp., fields on the upper right
                      labelled 'Red Marker' and 'Gauss Fit Mean'

               - If fit is deemed not good enough, you can correct the Gauss-Fit by:
                    - a Mouse-Left-Click to set left foot of peak
                    - a Mouse-Right-Click to set right foot of peak

               - The Red-Marker position serves as assistant to judge the goodness of the fit. It can be
                 moved with:
                    - mouse Middle clicks
                    - keys Left / Right in increments of 0.2 channel
                    - keys Alt-Left / Alt-Right in increments of 0.01 channel

               - To prepare calibration you need to fill the 'Channel' field of the isotope list:
                    - you can manually enter the channel value
                    - you can Drag-And-Drop the values from the red / green fields
                    - Easiest: mouse left click into the field to be filled, and press return. This will place
                      the 'Gauss Fit Mean' value into the selected field.

               - To calibrate click the 'Apply Calibration' button
                    - this will place the new calibration fit into the 'Calibration Fitting Result' space
                    - the calibration will use the highest Polynomial order possibel with the given set of
                      calibration point but only up to order 3. You can limit this to maximum of Linear,
                      Quadratic, of Cubic by selecting from the 'Max Fit Degree' drop-down list.

               - To use these values for the current session, click 'OK'

               - To additionally ave this to the spectro file, click 'OK&Save'
               """)

    CloseButton = QPushButton("Close")
    CloseButton.clicked.connect(lambda:  hdlg.done(0))

    # add single bottom buttons 'close'
    bbox = QDialogButtonBox()
    bbox.addButton(CloseButton,         QDialogButtonBox.ButtonRole.ActionRole)

    helpLabel = QLabel(helptxt)
    helpLabel.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

    helpLayout = QVBoxLayout()
    helpLayout.addWidget(helpLabel)
    helpLayout.addWidget(bbox)

    hdlg = QDialog()
    hdlg.setWindowIcon(g.iconGeigerLog)
    hdlg.setWindowTitle("Help Calibration")
    hdlg.setMinimumWidth(500)
    hdlg.setWindowModality     (Qt.WindowModality.WindowModal)   # can click multiple times for new graphs
    hdlg.setLayout(helpLayout)
    hdlg.exec()


#oncalib
def onCalibMouseClick(event):
    """"""

    #################################################################################
    def getYLeft(y):

        yLbottom, yLtop = cax1.get_ylim()
        yRbottom, yRtop = cax2.get_ylim()

        yR = y / (yRtop - yRbottom)
        yL = (yLtop - yLbottom) * yR + yLbottom

        return yL
    #################################################################################

    defname = "onCalibMouseClick: "

    xdata   = event.xdata                               # from 0 to max(Channel)
    ydata   = event.ydata                               # y from RIGHT y-Axis
    b       = event.button                              # 1=Left, 2=Middle, 3=Right
    btns    = event.buttons                             # is always == None
    d       = event.dblclick                            # not used here
    key     = event.key                                 # control, left, ...

    button  = ("Left", "Middle", "Right")[b - 1]        # mouse button

    if event.inaxes:
        ydata = getYLeft(ydata)
        if ydata is not None: ydata = 10**ydata if g.calibShowLog else ydata

        cdprint(defname, f"inaxes:  xdata:{xdata:<8.3f}  yLeft:{ydata:<8.3f}   b:{button:6s}  btns:{btns}  dbl:{d}  key:{str(key):<10s}  hasFocus:{g.canvasCalib.hasFocus()}")

        # # the click was in the white data area
        # if not g.canvasCalib.hasFocus():
        #     ydprint(defname, "Canvas has no FOCUS - setting it now")
        #     g.canvasCalib.setFocus()
        #     if g.debug: cocoo()

        # cdprint(defname, f"inaxes:  xdata:{xdata:<8.3f}  yLeft:{ydata:<8.3f}   b:{button:6s}  btns:{btns}  dbl:{d}  key:{str(key):<10s}  hasFocus:{g.canvasCalib.hasFocus()}")

        # clip
        if key == "control":
            if   "Left"  in button:  g.calibLeft[0]  = int(xdata)       # left Clip
            elif "Right" in button:  g.calibRight[0] = int(xdata)       # right Clip

            if g.calibRight[0] is not None:
                counts   = g.Counts                 [g.calibLeft[0] : g.calibRight[0] + 1]
                channels = range(0, len(g.Counts))  [g.calibLeft[0] : g.calibRight[0] + 1]
            else:
                counts   = g.Counts                 [g.calibLeft[0] : ]
                channels = range(0, len(g.Counts))  [g.calibLeft[0] : ]

            if g.calibRight[0] is None or g.calibLeft[0] is None: ChDelta = g.NAN
            else:                                                 ChDelta = g.calibRight[0] - g.calibLeft[0] + 1
            gdprint(defname, f"g.calibLeft: {g.calibLeft}   g.calibRight: {g.calibRight}  ChDelta:{ChDelta}")

            # just plot; no fitting
            plotGraphCalib(channels, counts)

        # fit
        elif key is None:
            if   g.spectroDataLen < 1000:     delta = 55
            elif g.spectroDataLen < 3000:     delta = 45
            elif g.spectroDataLen < 5000:     delta = 35
            elif g.spectroDataLen < 10000:    delta = 25
            else:                             delta = 15

            if "Middle" in button:
                newMean         = xdata
                g.calibLeftFit  = int(max(0,                xdata - delta)),     None
                g.calibRightFit = int(min(g.spectroDataLen, xdata + delta + 1)), None

                # g.redMarker.setText(f"{newMean:0.2f}")

            elif "Left" in button:
                newMean        = xdata + delta / 2
                g.calibLeftFit = int(xdata), ydata
                if g.calibRightFit[0] is None:  g.calibRightFit = int(min(g.spectroDataLen, xdata + delta + 1)), ydata

            elif "Right" in button:
                newMean         = xdata - delta / 2
                g.calibRightFit = int(xdata), ydata
                if g.calibLeftFit[0] is None:   g.calibLeftFit = int(max(0,                 xdata - delta)), ydata

            # if g.redMarker.text() == "":  g.redMarker.setText(f"{newMean:0.2f}")
            makeCalibGaussFits(newMean)

        else:
            cdprint(defname, f"in-axes:  b:'{button:6s}'  btns:{btns}  dbl:{d}  key:{str(key):<10s}  hasFocus:{g.canvasCalib.hasFocus()} ")
            burp()


def onCalibKeyPress(event):
    """on a cursor-key press"""

    return

    defname = "onCalibKeyPress: "
    # cdprint(defname, f"you pressed: event.key: {event.key}  event.xdata: {event.xdata}  event.ydata: {event.ydata}")

    deltaTime = time.time() - g.KeyPressTime
    # ydprint(defname, f"deltaTim {deltaTim0.2f}")

    if deltaTime >= 0.1:                                        # proceed only if key presses do NOT come too frequent
        g.KeyPressTime = time.time()

        MarkerValue = getMarkerValue()

        # if not event.inaxes: return
        if np.isnan(getMarkerValue()): return

        if   event.key == "right":      MarkerValue += 0.2
        elif event.key == "left":       MarkerValue -= 0.2
        elif event.key == "alt+right":  MarkerValue += 0.01
        elif event.key == "alt+left":   MarkerValue -= 0.01
        else:                           return

        # g.redMarker.setText(f"{MarkerValue:0.2f}")
        makeCalibGaussFits(MarkerValue)


def makeCalibGaussFits(mean):
    """"""

    defname  = "makeCalibGaussFits: "

    clipchannels = range(0, len(g.Counts)) [g.calibLeft[0] : g.calibRight[0] + 1]
    clipcounts   = g.Counts                [g.calibLeft[0] : g.calibRight[0] + 1]

    peak     = np.max(clipcounts)
    sigma    = 1
    lastmean = 0                                # last mean

    deltaClip = g.calibRight[0] - g.calibLeft[0] + 1
    mdprint(defname, f"INIT:  Clipleft: {g.calibLeft[0]}  Clipright: {g.calibRight[0]}   Delta:{deltaClip}  Red Marker:{mean:0.2f}")
    setIndent(1)

    leftX  = g.calibLeftFit[0]
    rightX = g.calibRightFit[0]

    fitChnl = range(0, len(g.Counts))  [leftX : rightX]
    fitCnts = g.Counts                 [leftX : rightX]

    if  g.calibLeftFit[1]  is None: leftY  = np.average(fitCnts[:5])
    else:                           leftY  = g.calibLeftFit[1]

    if  g.calibRightFit[1] is None: rightY = np.average(fitCnts[-5:])
    else:                           rightY = g.calibRightFit[1]

    # background
    calibBG  = np.linspace(leftY, rightY, len(fitCnts))        # make Background
    # calibBG  = np.linspace(0,   0,      len(fitCnts))        # make Background all zero
    fitCnts  = fitCnts - calibBG

    loopMax     = 10     # max number of loops
    for loopcounter in range(loopMax):
        # ydprint(defname, f"g.calibLeftFit[0]:     {g.calibLeftFit[0]}   g.calibRightFit[0]:{g.calibRightFit[0]}")

        while True: # assure more than 5 channels

            fitChnl = range(0, len(g.Counts))  [leftX : rightX]
            fitCnts = g.Counts                 [leftX : rightX]

            if  g.calibLeftFit[1]  is None: leftY  = np.average(fitCnts[:5])
            else:                           leftY  = g.calibLeftFit[1]

            if  g.calibRightFit[1] is None: rightY = np.average(fitCnts[-5:])
            else:                           rightY = g.calibRightFit[1]

            calibBG  = np.linspace(leftY, rightY, len(fitCnts))        # make Background
            # calibBG  = np.linspace(0,   0,      len(fitCnts))        # make Background all zero
            fitCnts  = fitCnts - calibBG

            # break

            if rightX - leftX > 5:
                break
            else:
                leftX  -= 5
                rightX += 5
                if leftX  < g.calibLeft[0] : leftX  = g.calibLeft[0]
                if rightX > g.calibRight[0]: rightX = g.calibRight[0]

        # end while - assure more than 5 channels


        ### GAUSSS FIT #########################################################
        response, rsquared = getGaussFit(fitChnl, fitCnts, peak, mean, sigma)
        ########################################################################

        if response != "Failure" and not np.isnan(rsquared):
            fitCoeff    = response[0]
            peak        = fitCoeff[0]
            mean        = fitCoeff[1]
            sigma       = fitCoeff[2]
            fitFlag     = response[4]
            fitSuccess  = True if fitFlag in (1, 2, 3, 4) else False

            try:    FWHM = sigma * 2.3548 / mean                         # FWHM in percent
            except: FWHM = g.NAN
            msg         = f"#{loopcounter:<2d}  L:{leftX:<4d} R:{rightX:4d}   Delta:{len(fitChnl):<3d}  peak:{peak:6.1f}  mean:{mean:6.4f}  sigma:{sigma:6.3f}  FWHM:{FWHM:0.2%}  fitSuccess:{fitSuccess}   r2:{rsquared:6.4f}"
            if fitSuccess:
                if rsquared > 0.9:  gdprint(defname, msg)
                else:               cdprint(defname, msg)
            else:
                rdprint(defname, msg)

            g.calibMeanGauss.setText(f"{mean:0.2f}")
            if abs(mean - lastmean) < 0.0001 and rsquared > 0.5:
                break           # good enough
            else:
                lastmean = mean
                sigma   *= 1.5
        else:
            fitCoeff    = None
            fitSuccess  = False
            oldsigma    = sigma
            sigma      *= 1.5
            rdprint(defname, f"#{loopcounter:<2d}  L:{leftX:<4d} R:{rightX:4d}   Delta:{len(fitChnl):<3d}              oldsigma:{oldsigma:6.3f}  sigma:{sigma:6.3f}  r2:{rsquared:6.4f}")

    # end for loopcounter

    g.calibFitResult = fitSuccess, fitChnl, fitCoeff, calibBG, mean, sigma, rsquared
    plotGraphCalib(clipchannels, clipcounts)

    setIndent(0)


#pc
def plotGraphCalib(channels=None, counts=None):
    """plot..."""

    global cax1, cax2   # needed in updatecursorpos

    # defname = "plotGraphCalib: "
    defname = gd(sys._getframe().f_code.co_name)

    if channels is None:    channels        = g.LastChannels
    else:                   g.LastChannels  = channels
    if counts is None:      counts          = g.LastCounts
    else:                   g.LastCounts    = counts

    if g.calibShowLog:
        newcounts = np.log10(counts)
        Ylabel    = "Log (Counts)"
    else:
        newcounts = counts.copy()
        Ylabel    = "Counts"

    plt.clf()                                                                               # REQUIRED !!!!!!!!!!!!!!!!!!

    ### get/set left and right Y-axis
    cax1 = plt.gca()                                                                        # left Y-axis
    cax2 = cax1.twinx()                                                                     # right Y-Axis

    # show grid
    if g.calibShowGrid:
        cax1.grid(visible=True, which='both', axis="both")
        cax1.grid(which='minor', color='#999', linestyle=':', lw=0.5)
        cax1.minorticks_on()

    # add labels to axis
    cax1.set_xlabel("Channel",                           fontsize=12, fontweight='bold')    # X-axis
    cax1.set_ylabel(Ylabel,                              fontsize=12, fontweight='bold')    # Yleft-axis
    cax2.set_ylabel("Energy [keV] | Channel Width [eV]", fontsize=12, fontweight='bold')    # Yright-axis

    # to prevent scientific notation and offset use
    cax1.yaxis.get_major_formatter().set_scientific(False)      # science
    cax1.yaxis.get_major_formatter().set_useOffset(False)       # offset
    cax1.ticklabel_format(style='plain', axis='y')              # do NOT use scientific notation
    cax2.yaxis.get_major_formatter().set_scientific(False)      # science
    cax2.yaxis.get_major_formatter().set_useOffset(False)       # offset
    cax2.ticklabel_format(style='plain', axis='y')              # do NOT use scientific notation

    ### set title -  a plt.suptitle is a "SUPER" title, not a sub title  ;-)
    RightTitle = os.path.basename(g.spectroDBPath) + f"  Chnls: {channels[0]}-{channels[-1]} ({len(channels)} of {len(g.Counts)})"
    plt.title(RightTitle, fontsize=10, fontweight='normal', loc = 'right')

    # plot spectrum
    marker      = "o"
    markersize  = 3
    if g.calibShowLine:
        # connecting line
        linewidth   = 0.5
        symbol      = "-"
    else:
        # separate dots
        linewidth   = 0
        symbol      = ""
    cax1.plot(channels, newcounts, symbol, color="blue", lw=linewidth, marker=marker, ms=markersize)

    # # plot Red Marker - if 'line' is g.NAN, nothing gets plotted
    # line = getMarkerValue()
    # cax1.plot([line, line], [0, cax1.get_ylim()[1] * 0.98], color="red", label="")         # plot the vertical Red Marker line
    # # mdprint(defname, f"lin {line}   ylimMin: {plt.ylim()[0]:0.3f}   ylimMax: {plt.ylim()[1]:0.3f}")

    # plot calibrated Energy and Channel Width and Legend
    if 1:
        if g.calibShowEW:
            plotChannel = np.array(range(channels[0], channels[0] + len(channels)))
            ECalib = PolynomValue(plotChannel, *g.spectroScale)
            WCalib = (ECalib[1:] - ECalib[:-1]) * 1000.0
            WCalib = np.append(WCalib, g.NAN)
            cax2.plot(channels, ECalib, "-",  lw=5, color="#ccc",   label="Energy - Calib")
            cax2.plot(channels, WCalib, "-",  lw=5, color="brown",  label="Channel-Width - Calib", alpha=0.5)
            cax2.plot(channels[0], 0,   "-",  lw=0, color="orange", label="") # invisible; to keep zero on yright-axis

        # plot the orig E + W
        if g.calibShowOrig:
            cax2.plot(channels, g.EnergyOrig   [channels[0] : channels[-1] + 1],           ":",  lw=2, color="black",  label="Energy - Orig")
            cax2.plot(channels, g.ChnlWidthOrig[channels[0] : channels[-1] + 1] * 1000,    "--", lw=2, color="brown",  label="Channel Width - Orig")

        if g.calibShowEW or g.calibShowOrig:
            cax2.legend()

    if g.calibFitResult is not None: # are data defined?
        fitSuccess, fitChnl, fitCoeff, calibBG, mean, sigma, rsquared = g.calibFitResult
        # print(defname, fitSuccess, fitChnl, fitCoeff, calibBG, mean, sigma, rsquared)

        if fitSuccess:
            FWHM  = sigma * 2.3548
            color = getFitColorPlot(rsquared)

            # gdprint(defname, f"Delta Mean: {mean - lastmean:0.5f}")
            fitResult = Gauss(fitChnl, *fitCoeff)

            if g.calibShowLog:
                # gdprint(defname, "LogScale requested")
                plotCnts = np.log10(fitResult + calibBG)
                plotbg   = np.log10(calibBG)
            else:
                # gdprint(defname, "LinearScale requested")
                plotCnts = fitResult + calibBG
                plotbg   = calibBG

            # irdprint(defname, f"lenfitChnl: {len(fitChnl)}   lenplotCnts: {len(plotCnts)}   lenplotbg: {len(plotbg)}")
            # plot curve
            cax1.plot        (fitChnl, plotCnts, "-", lw=4,    color=color, alpha=0.6)

            # fill under curve
            cax1.fill_between(fitChnl, plotCnts, plotbg      , color=color, alpha=0.2)

            fitText  = f"Fit r2: {rsquared:0.3f}  FWHM: {FWHM / mean:0.2%}"
            fitColor = "black"
        else:
            fitText  = f"Fit r2: {'Fitting failed!'}"
            fitColor = "red"
            g.calibMeanGauss.setText("")
            cax1.plot        (fitChnl, calibBG, "-", lw=4,    color="Grey", alpha=0.9)
            burp()

        # print on lower left of graph
        plt.figtext(0.005, 0.005, fitText,  backgroundcolor= "#C9F9F0", color=fitColor, fontsize=13, fontweight=1000)

    pushPlotToScreen(g.figCalib)


def pushPlotToScreen(figpointer):
    """make the plot visible"""

    figpointer.canvas.draw()                # REQUIRED !!!!!!!!!!
    # figpointer.canvas.flush_events()      # maybe not needed? I see no effect
    # figpointer.canvas.draw_idle()         # apparently not needed


def saveCalibGraph():
    """save the Calib graph to a (png) file"""

    defname = "saveCalibGraph: "

    sprint(headerSpec("Save Calibration Graph"))

    if g.spectroData is None or len(g.spectroData) <= 1:
        sprint(f"Cannot save - No Data\n")
    else:
        pngpath = g.spectroDBPath + ".Calib.png"
        plt.savefig(pngpath)
        sprint(f"Database: {g.spectroDBPath}")
        sprint(f"to File:  {pngpath}\n")

