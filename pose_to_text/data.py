from itertools import chain
from text_to_pose.data import get_dataset as get_single_dataset, TextPoseDataset


def get_dataset(**kwargs):
    datasets = [
        get_single_dataset(name="dicta_sign", **kwargs),
        # get_single_dataset(name="sign2mint", **kwargs)
    ]

    all_data = list(chain.from_iterable([d.data for d in datasets]))
    # TODO @AmitMY - 3D normalize hand and face
    return TextPoseDataset(all_data)
