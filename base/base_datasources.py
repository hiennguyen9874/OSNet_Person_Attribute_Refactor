import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), ".."))

import zipfile
import tarfile

from tqdm.auto import tqdm
from shutil import copy2

from utils import download_file_from_google_drive, download_with_url


class BaseDataSource(object):
    def __init__(self, root_dir, dataset_dir, phase=["train", "val", "test"], **kwargs):

        self.phase = phase
        self.root_dir = root_dir
        self.dataset_dir = dataset_dir

    def _exists(self, extract_dir):
        raise NotImplementedError

    def _extract(self, file_name, use_tqdm=True, pwd=None):
        r"""extract compressed file
        Args:
            use_tqdm (boolean): use tqdm process bar when extracting
        """
        file_path = os.path.join(self.root_dir, self.dataset_dir, "raw", file_name)
        extract_dir = os.path.join(
            self.root_dir,
            self.dataset_dir,
            "processed",
            "".join(file_name.split(".")[:-1]),
        )
        if self._exists(extract_dir):
            return
        print("Extracting...")
        pwd = bytes(pwd, "utf-8") if pwd != None else None
        try:
            tar = tarfile.open(file_path)
            os.makedirs(extract_dir, exist_ok=True)
            if use_tqdm:
                for member in tqdm(
                    iterable=tar.getmembers(),
                    total=len(tar.getmembers()),
                    desc=file_name,
                ):
                    tar.extract(member=member, path=extract_dir, pwd=pwd)
            else:
                tar.extractall(path=extract_dir, pwd=pwd)
            tar.close()
        except:
            zip_ref = zipfile.ZipFile(file_path, "r")
            if use_tqdm:
                for member in tqdm(
                    iterable=zip_ref.infolist(),
                    total=len(zip_ref.infolist()),
                    desc=file_name,
                ):
                    zip_ref.extract(member=member, path=extract_dir, pwd=pwd)
            else:
                zip_ref.extractall(path=extract_dir, pwd=pwd)
            zip_ref.close()
        print("Extracted!")

    def _download(
        self, file_name, url=None, dataset_id=None, file_path=None, use_tqdm=True
    ):
        r"""download file from google drive.
        Args:
            dataset_id (str): id of file on google drive. guide to get it (https://www.wonderplugin.com/wordpress-tutorials/how-to-apply-for-a-google-drive-api-key/)
            use_tqdm (boolean): use tqdm process bar when downloading
        """
        os.makedirs(os.path.join(self.root_dir, self.dataset_dir, "raw"), exist_ok=True)
        if dataset_id != None:
            print("Downloading...")
            try:
                try:
                    download_file_from_google_drive(
                        dataset_id,
                        os.path.join(self.root_dir, self.dataset_dir, "raw"),
                        use_tqdm,
                    )
                except:
                    url = (
                        "https://www.googleapis.com/drive/v3/files/"
                        + dataset_id
                        + "?alt=media&key=AIzaSyBEp1hj-WxRxAezSd5sGfPmWnLbuxuxSvI"
                    )
                    download_with_url(
                        url,
                        os.path.join(self.root_dir, self.dataset_dir, "raw"),
                        file_name,
                        use_tqdm,
                    )
            except:
                try:
                    if os.path.exists(
                        os.path.join(self.root_dir, self.dataset_dir, "raw", file_name)
                    ):
                        os.remove(
                            os.path.join(
                                self.root_dir, self.dataset_dir, "raw", file_name
                            )
                        )
                    download_file_from_google_drive(
                        dataset_id,
                        os.path.join(self.root_dir, self.dataset_dir, "raw"),
                        use_tqdm,
                    )
                except:
                    if os.path.exists(
                        os.path.join(self.root_dir, self.dataset_dir, "raw", file_name)
                    ):
                        os.remove(
                            os.path.join(
                                self.root_dir, self.dataset_dir, "raw", file_name
                            )
                        )
                    url = (
                        "https://www.googleapis.com/drive/v3/files/"
                        + dataset_id
                        + "?alt=media&key=AIzaSyBEp1hj-WxRxAezSd5sGfPmWnLbuxuxSvI"
                    )
                    download_with_url(
                        url,
                        os.path.join(self.root_dir, self.dataset_dir, "raw"),
                        file_name,
                        use_tqdm,
                    )
            print("Downloaded!")
        elif url != None:
            download_with_url(
                url,
                os.path.join(self.root_dir, self.dataset_dir, "raw"),
                file_name,
                use_tqdm,
            )
        elif file_path != None:
            print("Copying data...")
            copy2(
                file_path,
                os.path.join(self.root_dir, self.dataset_dir, "raw", file_name),
            )
            print("Copied!")
        else:
            if not os.path.exists(
                os.path.join(self.root_dir, self.dataset_dir, "raw", file_name)
            ):
                raise FileExistsError(
                    "please download file %s into %s"
                    % (file_name, os.path.join(self.root_dir, self.dataset_dir, "raw"))
                )

    def get_data(self, phase="train"):
        r"""get data, must return list of (image_path, label)"""
        raise NotImplementedError

    def get_phase(self):
        r"""get list of phase."""
        return self.phase

    def _check_file_exits(self):
        r"""check all image in datasource exists"""
        for phase in self.phase:
            for path, label in self.get_data(phase):
                if not os.path.exists(path):
                    raise FileExistsError

    def show_some_image(self, num_image, num_per_row=10):
        import cv2
        import math
        import matplotlib
        import matplotlib.pyplot as plt
        import numpy as np

        from utils import imread

        all_rand_path = np.random.choice(range(len(self.get_data("train"))), num_image)
        all_rand_image = [
            cv2.resize(imread(self.get_data("train")[x][0]), (128, 256))
            for x in all_rand_path
        ]
        fig, ax = plt.subplots(math.ceil(num_image / num_per_row), num_per_row)
        if math.ceil(num_image / num_per_row) == 1:
            for j in range(num_per_row):
                ax[j].axis("off")
                ax[j].imshow(all_rand_image[j])
        else:
            # fig.tight_layout()
            for i in range(math.ceil(num_image / num_per_row)):
                for j in range(num_per_row):
                    ax[i][j].axis("off")
                    if i * num_per_row + j < num_image:
                        ax[i][j].imshow(all_rand_image[i * num_per_row + j])
        # plt.show()
        # matplotlib.use("pgf")
        # matplotlib.rcParams.update({
        #     "pgf.texsystem": "pdflatex",
        #     'font.family': 'serif',
        #     'text.usetex': True,
        #     'pgf.rcfonts': False,
        # })
        plt.savefig("{}_show.pdf".format(self.dataset_dir))
