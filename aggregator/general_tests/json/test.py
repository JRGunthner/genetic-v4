import pandas as pd

# d = {'col_1': [3, 2, 1, 0], 'col_2': ['a', 'b', 'c', 'd']}
# d = {'col1': [1, 2], 'col2': [3, 4]}
# df = pd.DataFrame(data = d)
df = pd.DataFrame(data={'col1': [1, 2],
                        'col2': [0.5, 0.75]},
                  index=['row1', 'row2'])
print(df)
