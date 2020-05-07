from    PyQt5.QtWidgets                     import  QApplication, QMainWindow   ,QMenu      ,QVBoxLayout    ,\
                                                    QSizePolicy , QMessageBox   ,QWidget    ,QPushButton    ,\
                                                    QGroupBox   , QGridLayout   ,QHBoxLayout,QCheckBox      ,\
                                                    QComboBox   , QListWidget   ,QLineEdit  ,QLabel         ,\
                                                    QScrollArea , QTabWidget    ,QCalendarWidget
from    PyQt5.QtGui                         import  QIcon
from    PyQt5                               import  QtWidgets   , QtGui         , QtCore
from    matplotlib.backends.backend_qt5agg  import  FigureCanvasQTAgg       as FigureCanvas
from    matplotlib.backends.backend_qt5agg  import  NavigationToolbar2QT    as NavigationToolbar
from    matplotlib.figure                   import  Figure
from    pandas.plotting                     import  register_matplotlib_converters
# mpl_finance deprecated
# Instead use mplfinance
#from    mpl_finance                          import  candlestick2_ohlc       , candlestick_ohlc
from    collections                         import  OrderedDict

import  mplfinance
import  matplotlib.dates                    as      mdates
import  saltools.misc                       as      sltm
import  matplotlib.pyplot                   as      plt
import  pandas                              as      pd 

import  traceback
import  engine
import  random
import  json
import  sys


register_matplotlib_converters()

CONFIG_PATH = "ui_config.json"
CONFIGS     = sltm.g_config(CONFIG_PATH)

def plot_ohlc   (
    df                  ,
    axes        = None  ):
    show        = False
    if not axes:
        show    = True
        fig     = plt.figure(figsize=(5, 4), dpi=100)
        axes    = fig.add_subplot(111)

    df          = df.reset_index()
    df["date"]  = df["date"].apply(mdates.date2num)
    axes.xaxis_date()
    axes.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H'))
    axes.tick_params(labelrotation=45, labelsize= 7)
    cl = candlestick_ohlc(
        ax          = axes                      ,
        quotes      = df.values   ,
        width       = 0.4           , 
        colorup     = '#77d879'     ,
        colordown   = '#db3f3f'     )
    
    if show:
        fig.show()
    else :
        return axes
def plot_htf    (
    df                  ,
    supply_start        , 
    supply_end          , 
    demand_start        , 
    demand_end          ,
    parts               ,
    axes        = None  ):
    print(df, supply_start, supply_end, demand_start, demand_end, parts)
    show        = False
    if not axes:
        show    = True
        fig     = plt.figure(figsize=(5, 4), dpi=100)
        axes    = fig.add_subplot(111)
    plot_ohlc(df, axes= axes)
    
    if      demand_start != None    :
        axes.axvline(x= demand_start  , alpha= .2, color= 'green'    )
        axes.axvline(x= demand_end    , alpha= .2, color= 'green'    )

    if      supply_start != None    :
        axes.axvline(x= supply_start  , alpha= .2, color= 'red'      )
        axes.axvline(x= supply_end    , alpha= .2, color= 'red'      )

    if      parts != None   : 
        for part in parts:
            axes.axhline(y= part[0]     , alpha= .2, color= 'black'  )
        axes.axhline    (y= parts[-1][1], alpha= .2, color= 'black'  )

    if show:
        fig.show()
    else :
        return axes
def plot_itf    (
    df          ,
    axes = None ):
    show        = False
    if not axes:
        show    = True
        fig     = plt.figure(figsize=(5, 4), dpi=100)
        axes    = fig.add_subplot(111)

    cl = candlestick2_ohlc(ax = axes, opens = df['open'], highs = df['high'], lows = df['low'], closes = df['close'], width = 0.4,  colorup = '#77d879', colordown = '#db3f3f')

    axes.plot(df['ema'].values, label= 'EMA', color='red'      )
    axes.plot(df['sma'].values, label= 'SMA', color='green'    )

    axes.set_xticklabels(df.index, fontsize = 6, rotation = -90)
    axes.legend()
        
    if show:
        fig.show()
    else :
        return axes

def plot_ltf(df, d_zones, s_zones, axes = None):
    show = False
    if not axes:
        show = True
        fig  = plt.figure(figsize=(5, 4), dpi=100)
        axes = fig.add_subplot(111)
    cl = candlestick2_ohlc(ax = axes, opens = df['open'], highs = df['high'], lows = df['low'], closes = df['close'], width = 0.4, colorup = '#77d879', colordown = '#db3f3f')

    axes.set_xticklabels(df.index, fontsize = 6, rotation = -90)
        
    for dz in d_zones:
        axes.axvline(x= list(df.index).index(dz[0]), alpha= .2, color= 'green')
        axes.axvline(x= list(df.index).index(dz[1]), alpha= .2, color= 'green')
    for sz in s_zones:
        axes.axvline(x= list(df.index).index(sz[0]), alpha= .2, color= 'red')
        axes.axvline(x= list(df.index).index(sz[1]), alpha= .2, color= 'red')

class WidgetPlot(QWidget):
    def __init__(self, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)
        self.setLayout(QVBoxLayout())
        self.canvas = PlotCanvas(self)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.layout().addWidget(self.toolbar)
        self.layout().addWidget(self.canvas)
class PlotCanvas(FigureCanvas):

    def __init__(self, parent = None, width = 5, height = 4, dpi = 100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def plot_htf(self, df, supply_start, supply_end, demand_start, demand_end, parts):
        self.axes.clear()
        plot_htf(df,supply_start, supply_end, demand_start, demand_end,parts, self.axes)
        self.draw()
    def plot_itf(self, dfi):
        self.axes.clear()
        plot_itf(dfi, self.axes)
        self.draw()
    def plot_ltf(self, dfl, d_zones, s_zones):
        self.axes.clear()
        plot_ltf(dfl, d_zones, s_zones, self.axes)
        self.draw()

class App(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'GUI'
        self.left = 100
        self.top = 100
        self.width = 640
        self.height = 480
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.create_layout()

        self.show()
    def create_tabs(self):
        self.tabs           = QTabWidget()



        self.tab1   = WidgetPlot()
        self.tab2   = WidgetPlot()
        self.tab3   = WidgetPlot()

        self.canvas_htf     = self.tab1.canvas
        self.canvas_itf     = self.tab2.canvas
        self.canvas_ltf     = self.tab3.canvas


        self.tabs.addTab(self.tab1,'HTF')
        self.tabs.addTab(self.tab2,'ITF')
        self.tabs.addTab(self.tab3,'LTF')

        self.tabs_layout    = QVBoxLayout()
        self.tabs_layout.addWidget(self.tabs)
        self.plots_combo    = QComboBox()
        self.plots_combo.currentTextChanged.connect(self.new_plot)
        self.tabs_layout.addWidget(self.plots_combo)

        return self.tabs_layout
    def create_layout(self):      
        def create_combo_configs():
            configs_combo = QComboBox()
            for x in CONFIGS :
                configs_combo.addItem(x)
            return configs_combo
        def create_combo_asset():
            asset_combo = QComboBox()
            asset_combo.addItem('Stocks')
            return asset_combo
        def create_combo_frame():
            frame_combo = QComboBox()
            for x in engine.TIME_FRAMES:
                frame_combo.addItem(x)
            return frame_combo
        def create_combo_frq():
            frq_combo = QComboBox()
            for x in engine.FREQUENCIES:
                frq_combo.addItem(x)
            return frq_combo
        def create_combo_direction():
            d_combo = QComboBox()
            for x in engine.DIRECTIONS:
                d_combo.addItem(x)
            return d_combo

        self.window_layout  = QHBoxLayout()
        self.setLayout(self.window_layout)

        self.window_layout.addLayout(self.create_tabs())
        
        self.options_box    = QVBoxLayout()
        v_widget            = QWidget()
        v_widget.setLayout(self.options_box)
        scroll = QScrollArea()
        scroll.setWidget(v_widget)
        scroll.setWidgetResizable(True)
        scroll.setFixedWidth(200)
        self.window_layout.addWidget(scroll)


        self.options = OrderedDict([
            ('config_l'             , QLabel('F00A- Config')            ),
            ('config'               , create_combo_configs()            ),
            
            ('config_id_l'          , QLabel('F00B-Config id')          ),
            ('config_id'            , QLineEdit('')                     ),

            ('ticker_l'             , QLabel('F00C-Ticker')             ),
            ('ticker'               , QLineEdit('')                     ),

            ('asset_l'              , QLabel('F01- Asset Class')        ),
            ('asset'                , create_combo_asset()              ),

            ('time_frame_l'         , QLabel('F02- Higher Time Frame')  ),
            ('time_frame'           , create_combo_frame()              ),

            ('direction_l'          , QLabel('F03- Trade Direction')    ),
            ('direction'            , create_combo_direction()          ),

            ('s_date_l'             , QLabel('F04A-Start Date YYYY-MM-DD')),
            ('s_date'               , QLineEdit('')                     ),

            ('e_date_l'             , QLabel('F04B-End Date')           ),
            ('e_date'               , QLineEdit('')                     ),

            ('htf_range_l'          , QLabel('F05-HTF Range')           ),
            ('htf_range'            , QLineEdit('200')                  ),

            ('htf_legin_value_l'    , QLabel('F06A-HTF Legin Value')    ),
            ('htf_legin_value'      , QLineEdit('40')                   ),
            ('htf_legout_value_l'   , QLabel('F06B-HTF Legout Value')   ),
            ('htf_legout_value'     , QLineEdit('3')                    ),
            ('htf_DZlegin_ratio_l'    , QLabel('F06C-HTF DZ Legin %')   ),
            ('htf_DZlegin_ratio'      , QLineEdit('.60')                ),
            ('htf_SZlegin_ratio_l'    , QLabel('F06C-HTF SZ Legin %')   ),
            ('htf_SZlegin_ratio'      , QLineEdit('.50')                ),
            
            ('htf_DZlegout_ratio_l'   , QLabel('F06D-HTF DZ Legout %')  ),
            ('htf_DZlegout_ratio'     , QLineEdit('.60')                ),
            ('htf_SZlegout_ratio_l'   , QLabel('F06D-HTF SZ Legout %')  ),
            ('htf_SZlegout_ratio'     , QLineEdit('.60')                ),

            ('htf_DZbase_ratio_l'     , QLabel('F07-HTF DZ Base %')     ),
            ('htf_DZbase_ratio'       , QLineEdit('.20')                ),
            ('htf_SZbase_ratio_l'     , QLabel('F07-HTF SZ Base %')     ),
            ('htf_SZbase_ratio'       , QLineEdit('.20')                ),
            
            ('ltf_range_l'          , QLabel('F08-LTF Range')           ),
            ('ltf_range'            , QLineEdit('100')                  ),

            ('ltf_legin_value_l'    , QLabel('F09A-LTF Legin Value')    ),
            ('ltf_legin_value'      , QLineEdit('5')                    ),
            ('ltf_legout_value_l'   , QLabel('F09B-LTF Legout Value')   ),
            ('ltf_legout_value'     , QLineEdit('5')                    ),

            ('ltf_DZlegin_ratio_l'    , QLabel('F09C-LTF DZ Legin %')   ),
            ('ltf_DZlegin_ratio'      , QLineEdit('.80')                ),
            ('ltf_SZlegin_ratio_l'    , QLabel('F09C-LTF SZ Legin %')   ),
            ('ltf_SZlegin_ratio'      , QLineEdit('.80')                ),

            ('ltf_DZlegout_ratio_l'   , QLabel('F09D-LTF DZ Legout %')  ),
            ('ltf_DZlegout_ratio'     , QLineEdit('.80')                ),
            ('ltf_SZlegout_ratio_l'   , QLabel('F09D-LTF SZ Legout %')  ),
            ('ltf_SZlegout_ratio'     , QLineEdit('.80')                ),

            ('ltf_DZbase_ratio_l'     , QLabel('F10-LTF DZ Base % ')    ),
            ('ltf_DZbase_ratio'       , QLineEdit('.30')                ),
            ('ltf_SZbase_ratio_l'     , QLabel('F10-LTF SZ Base % ')    ),
            ('ltf_SZbase_ratio'       , QLineEdit('.30')                ),
            
            ('frequency_l'          , QLabel('F11- Execution Frequency')),
            ('frequency'            , create_combo_frq()                ),

            ('execution_time_l'     , QLabel('F12-Execution time')      ),
            ('execution_time'       , QLineEdit('00:00')                ),

            ('legout_lh_l'          , QLabel('FX00-Legout must be Lowest/Hightest')  ),
            ('legout_lh'            , QCheckBox()                       ),

            ('enable_itf_l'         , QLabel('Enable ITF')              ),
            ('enable_itf'           , QCheckBox()                       ),

            ('save_config'          , QPushButton('Save config')        ),
            ('run'                  , QPushButton('Run')                ),
            ('run_once'             , QPushButton('Run Once')           ),
            ])

        self.options['run'].clicked.connect(self.run)
        self.options['save_config'].clicked.connect(self.save_config)
        self.options['config'].currentTextChanged.connect(self.new_config)

        if len(CONFIGS):
            self.new_config(list(CONFIGS.keys())[0])

        for v in self.options.values():
            self.options_box.addWidget(v)
    def g_values(self):
        return {x: self.g_value(x) for x in self.options if \
            (x not in ['run', 'save_config', 'config_id', 'config', 'run_once'] and x[-2:] != '_l')}
    def new_plot(self, key):
        if not self.results.get(key):
            return
        pair                ,\
            dfh             ,\
            supply_start    ,\
            supply_end      ,\
            demand_start    ,\
            demand_end      ,\
            parts           ,\
            htf_score       ,\
            dfi             ,\
            itf_score       ,\
            dfl             ,\
            d_zones         ,\
            s_zones         = self.results[key]
            
        self.canvas_htf.plot_htf(
                dfh                 ,
                supply_start        , 
                supply_end          , 
                demand_start        , 
                demand_end          ,
                parts               )           
        #self.canvas_itf.plot_itf(dfi)
        #self.canvas_ltf.plot_ltf(dfl, d_zones, s_zones)
    def run(self):
        #self.save_config()
        try :
            self.results = engine.Engine(**self.g_values()).run()
            self.plots_combo.clear()
            for key in self.results:
                self.plots_combo.addItem(key)
        except Exception as e:
            msg = QMessageBox()
            msg.setText(traceback.format_exc())
            msg.exec()
    def new_config(self, x):
        if not x in CONFIGS:
            return 
        for y in CONFIGS[x]:
            self.s_value(y, CONFIGS[x][y])
        self.s_value('config_id',  x)   
    def save_config(self):
        vals_dict = self.g_values()
        CONFIGS[self.g_value('config_id')] = vals_dict

        with open(CONFIG_PATH, 'w') as f:
            json.dump(CONFIGS, f)
        self.options['config'].clear()
        for x in CONFIGS:
            self.options['config'].addItem(x)
    def s_value(self, x, value):
        widget = self.options[x]
        if issubclass(widget.__class__,   QLineEdit) :
            widget.setText(value)
            return
        if issubclass(widget.__class__,   QCheckBox) :
            widget.setChecked(value)
            return
        if issubclass(widget.__class__,   QComboBox) :
            index = widget.findText(value, QtCore.Qt.MatchFixedString)
            if index >= 0:
                widget.setCurrentIndex(index)
            return
    def g_value(self, x):
        widget = self.options[x]
        if issubclass(widget.__class__,   QLineEdit) :
            return widget.text()
        if issubclass(widget.__class__,   QCheckBox) :
            return widget.isChecked()
        if issubclass(widget.__class__,   QComboBox) :
            return widget.currentText()

def main():
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()