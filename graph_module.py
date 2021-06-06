import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import seaborn as sns


def plot_chart(df, title : str, x_label : str, y_label : str, options : dict) :
    
    fig = plt.figure(figsize=(10, 5), dpi=200)
    ax = plt.gca()
    # 차트 제목
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)

    df.plot(kind=options.type if options.type else 'bar', ax=ax, 
            stacked = options.stack if options.stack else True)
    return fig


def hist_chart(df, title : str, x_label : str, y_label : str, options : dict) :
    
    fig = plt.figure(figsize=(10, 5), dpi=200)
    ax = plt.gca()
    # 차트 제목
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)

    plt.hist(df['any'], bins = options.bins if options.bins else 10, 
                density=options.density if options.density else True, 
                color=options.color if options.color else 'blue', 
                histtype=options.type if options.type else 'bar')
    return fig


def scatter_plot(df, title : str, x_label : str, y_label : str, options : dict) :   
    fig = plt.figure(figsize=(10, 5), dpi=200)
    ax = plt.gca()
    # 차트 제목
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)

    sns.scatterplot(x = options.x if options.x else 0 , 
                y=options.y if options.y else 0, 
                hue=options.hue if options.hue else None, # different colors by group
                style=options.style if options.style else None, # different shapes by group
                s=options.s if options.s else 20, # default size is 20
                data=df)
    return fig


