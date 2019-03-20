# Imports
import torch
from torch.utils.data import DataLoader, Dataset
from torchvision import datasets
import os
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore', category=UserWarning)


class FerDataset(Dataset):
    """
    Custom pytorch `Dataset` class implementation to load fer images dataset.
    This class loads the images from the original fer raw csv file
    """

    def __init__(self, data_dir, flag, transform=None):

        """

        :param data_dir: path to the csv file containing the data
        :param flag: string indicating which slice of data to load. In the fer csv file, there are 3 sets of data:
                `Training`, `PublicTest`, `PrivateTest`
        :param transform: torchvision `transforms.Compose` object containing transformation to be applied to images
        """

        self.data = self._read_csv(data_dir, flag)
        self.transform = transform

    def __len__(self):
        """

        :return: the size of the dataset
        """
        return self.data.shape[0]

    def __getitem__(self, idx):
        """

        :param idx: retrieve the image and label at position `idx`
        :return: 2 pytorch tensors representing the image and the label resp.
        """

        im = np.array([
            int(i) for i in self.data['pixels'].iloc[idx].split(' ')
        ]).reshape((48, 48))

        lab = np.array(self.data['emotion'].iloc[idx]).astype(np.uint8)

        if self.transform is not None:
            im = self.transform(im).to(torch.float32)

        lab = torch.from_numpy(lab).long()

        return im, lab

    @staticmethod
    def _read_csv(path_to_csv, flag='Training'):
        df = pd.read_csv(path_to_csv, sep=',')
        return df.loc[df['Usage'] == flag]


def get_fer_dataloader(batch_size=256, data_dir='./fer2013.csv', flag='Training', from_csv=True,
                       data_transforms=None):

    """
    Utility function to create a pytorch `DataLoader` to use for training

    :param batch_size: int representing the size of data batches
    :param data_dir: directory containing the data, the data could either be the path to the raw csv file,
            or a directory containing 3 subdirectories : `Training`, `PublicTest` and `PrivateTest`, each containing
            resp. train, validation and test image files.
    :param flag: string representing the set to be loaded among : `Training`, `PublicTest` and `PrivateTest`
    :param from_csv: boolean telling wether the data are from the raw csv file, or from image files
    :param data_transforms: torchvision `transforms.Compose` object containing transformation to be applied to images
    :return: pytorch `DataLoader` object to iterate through and get batches
    """

    if from_csv:
        image_dataset = FerDataset(data_dir, flag, data_transforms)
    else:
        image_dataset = datasets.ImageFolder(os.path.join(data_dir, flag), data_transforms)

    shuffle = True if flag == 'Train' else False
    dataloader = DataLoader(image_dataset, batch_size=batch_size, num_workers=8, shuffle=shuffle)
    return dataloader
