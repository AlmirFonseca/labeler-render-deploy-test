import json
import os


class Labels:
    def __init__(self, labels_path='data/labels.json'):
        self.labels = []
        self.labels_path = labels_path
        self.read_labels()

    def add_label(self, label: tuple[int, int, str]) -> None:
        """
        Add a new label to labels list

        Parameters
        ----------
        label : tuple(int, int, str)
            Label to be added. Format: (label_start, label_end, label_name)
        """
        appended = False
        # If labels list is empty, add label
        if len(self.labels) == 0:
            self.labels.append(label)
            appended = True
        # If labels list has one label or more
        else:
            # Check if new label is before the first label
            if label[1] < self.labels[0][0]:
                self.labels.insert(0, label)
                appended = True
            # If labels list has more than one label
            if len(self.labels) > 1:
                # Check if new label is between pairs of labels
                for label_pair in [(self.labels[i], self.labels[i+1]) for i in range(len(self.labels)-1)]:
                    first_label, second_label = label_pair
                    if (first_label[1] < label[0] < second_label[0] and
                        first_label[1] < label[1] < second_label[0]):
                        self.labels.insert(self.labels.index(second_label), label)
                        appended = True
                        break
            # Check if new label is after the last label
            if label[0] > self.labels[-1][1]:
                self.labels.append(label)
                appended = True
        # If label was not appended, raise error
        if not appended:
            raise ValueError('Label could not be appended. '
                             'Check if label is overlapping with another label(s). ')
        self.save_labels()
      
    @property
    def data(self) -> list[tuple[int, int, str]]:
        return self.labels

    def read_labels(self) -> None:
        if not os.path.exists(self.labels_path):
            self.save_labels()
        with open(self.labels_path, 'r') as f:
            self.labels = json.load(f)
    
    def save_labels(self) -> None:
        with open(self.labels_path, 'w') as f:
            json.dump(self.labels, f, indent=4)
