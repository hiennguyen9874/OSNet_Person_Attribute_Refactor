import os
import torch
import numpy as np
import random
import pandas as pd
import matplotlib.pyplot as plt

import sys
sys.path.append('.')


from utils import aggregate

def plot_loss_accuracy(dpath, list_dname, path_figure, title = None, low_ratio = .05, high_ratio = .95, com=0):
    """ Plot loss and accuracy from tensorboard file
    Args:
        dpath (str): path to folder contain (eg: saved/logs)
        list_dname (list(str)): list of run_id to plot.
        output_path (str): path to save csv file after concat logs from different run time
        title (str): title for figure
        low, high (float [0, 1]): ratio for remove outlier
        com (float [0, 1]): ratio for smooth line
    """
    dict_data_frame, list_part = aggregate(dpath, list_dname)

    fig, ax = plt.subplots(nrows=1, ncols=len(list_part[0]), figsize=(25, 10))
    
    for i in range(len(list_part[0])):
        colors = ['red', 'green']
        list_quant_df = []
        for j in range(len(list_part[1])):
            df = dict_data_frame[list_part[0][i]][list_part[1][j]]
            list_quant_df.append(df.quantile([low_ratio, high_ratio]))
        low = min(*[x.loc[low_ratio, 'Value'] for x in list_quant_df])
        high = max(*[x.loc[high_ratio, 'Value'] for x in list_quant_df])
        for j in range(len(list_part[1])):
            df = dict_data_frame[list_part[0][i]][list_part[1][j]]
            # remove outlier
            df = df[(df['Value'] >= low) & (df['Value'] <= high)]
            # smoothing
            df['Value'] = df['Value'].ewm(com=com).mean()
            # plot
            df.plot.line(
                x='Step',
                y ='Value',
                label=list_part[1][j],
                color=colors[j],
                ax=ax[i])
            
        ax[i].set_title(list_part[0][i])
        ax[i].set_xlabel('Epoch')
        # Hide the right and top spines
        ax[i].spines['right'].set_visible(False)
        ax[i].spines['top'].set_visible(False)
        # Only show ticks on the left and bottom spines
        ax[i].yaxis.set_ticks_position('left')
        ax[i].xaxis.set_ticks_position('bottom')
        # show grid
        ax[i].grid()

    if title != None:
        fig.suptitle(title)
    # plt.show()
    fig.savefig(path_figure, dpi=300)

def plot(path, run_id, title):
    return plot_loss_accuracy(
        dpath=path,
        list_dname=[run_id],
        path_figure=os.path.join(path, run_id, 'plot.png'),
        title=title,
        low_ratio=0.05,
        high_ratio=0.95,
        com=0.0)

def show_image(distances, queryset, testset, k=5, num_image=5, size_img=(2.5, 5)):
    plt.figure(figsize=((k+1)*size_img[0], num_image*size_img[1]))
    to_show = []
    for i in range(num_image):
        index = random.randint(0, len(distances)-1)
        query = queryset.get_img(index)
        topk = distances[index].topk(k, largest=False)
        to_display = [np.array(query)]
        for distance, index in zip(topk.values, topk.indices):
            img = np.array(testset.get_img(int(index.data)))
            to_display.append(img)
        to_display = np.concatenate(to_display, axis=1)
        to_show.append(to_display)
    to_show = np.concatenate(to_show, axis=0)
    plt.imshow(to_show)
    plt.axis('off')
    plt.show()

if __name__ == "__main__":
    plot(os.path.join('saved', 'logs'), '0708_043423', '0708_043423: osnet, CEL_Sigmoid, ppe')


    