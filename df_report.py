#!/usr/bin/python3

import sys
import numpy     as     np
import pandas    as     pd
from   tabulate  import tabulate
import argparse

def df_report(filename,
                    sep          = ';',
                    encoding     = "utf-8",
                    max_list_len = 10,
                    index        = None,
                    target       = None) :
    """
    df_report : 
    """

    print ("File name          : ", filename)

    df = pd.read_csv(filename, sep = sep, encoding = encoding, engine = 'c')

    tablefmt = "psql"

    rows_nb, cols_nb = df.shape
    cells_nb = rows_nb * cols_nb

    nb_dec = int(np.log10(rows_nb)) + 1
    fmt_int = "{:" + str(nb_dec) + "d}"
    fmt_pc = "{:" + str(nb_dec + 2) + "." + str(nb_dec - 2) + "f}"
    #print("format nombre      : ", fmt_int)  # for debugging purpose only
    #print("format pourcentage : ", fmt_pc)   # for debugging purpose only

    print("Rows number    : ", fmt_int.format(rows_nb))
    print("Columns number : ", fmt_int.format(cols_nb))
    print("Cells          : ", cells_nb)

    print ()

    ######################################################################
    # Display info of columns : name, type, number of na and ratio of na
    ######################################################################
    headers = ("Feature", "Type", "Na", "ratio(%)")
    lines = []
    lines2 = []
    max_name_width = 0
    total_nb_na = 0

    for col in df.columns :
        name_width = len(col)
        if name_width > max_name_width :
            max_name_width = name_width
        nb_na = df[col].isnull().sum()
        total_nb_na += nb_na
        lines.append ([col, df.dtypes[col], nb_na, 100.*nb_na / rows_nb])

    for col in df.columns :
        nb_na = df[col].isnull().sum()
        pc_s = "" if nb_na == 0 else fmt_pc.format(100.*nb_na / rows_nb)
        lines2.append ([col, df.dtypes[col], nb_na, pc_s])

    print (tabulate(lines2,
                    headers  = ["Column", "Type", "Nulls", "Prop (%)"],
                    colalign = ("left", "left", "right", "right"),
                    tablefmt = tablefmt))

    ######################################################################
    # Display stats of values of each column :
    # describe(), value_counts, values according to type of column and 
    # values.
    ######################################################################
    icol = 0
    for col in df.columns :
        nb_null = int(df[col].isnull().sum())
        #nb_null_FR = df[col].isnull().sum()
        typecol = str(df.dtypes.iloc[icol])
        print ()
        print ("==================")
        print ()
        print ("  " + col)
        print()
        print ("Type        : ", df.dtypes[col])
        print ("nulls       : {:d}".format(nb_null))
        print ("Proportion  : ", 100.*nb_null/rows_nb, "%")
        print ()

        if typecol == 'float64'  or typecol =='int64':
            print (tabulate(pd.DataFrame(df[col].describe()),
                            headers=["stat", "Value"],
                            tablefmt = tablefmt))

        if typecol == 'bool' :
            true_nb  = df[col].sum()
            false_nb = (df[col]==False).sum()
            null_nb  = df[col].isnull().sum()
            lines = [["True", true_nb, 100.*true_nb/rows_nb], ["False", false_nb, 100.*false_nb/rows_nb], ["Null", null_nb, 100.*null_nb/rows_nb]]
            print (tabulate (lines,
                             headers = ["Values", "Count", "Prop (%)"],
                             tablefmt = tablefmt))

        if typecol == 'object' or typecol == 'int64' :
            print ("Nombre de valeurs uniques  : ", df.shape[0] - df[col].duplicated().sum())
            print ("Nombre de valeurs répétées : ", df[col].duplicated().sum())

            cumul_nb = 0
            value_counts = pd.DataFrame(df[col].value_counts())
            categories_nb = value_counts.shape[0]
            if categories_nb <= max_list_len :
                lines_nb = categories_nb
            else : # List has to be truncated
                lines_nb = max_list_len
                value_counts = value_counts.head(lines_nb)

            lines = []
            for i in range(lines_nb) :
                mod_nb = int(value_counts.values[i])
                lines.append([value_counts.index[i], mod_nb, fmt_pc.format(100.*mod_nb/rows_nb)])
                cumul_nb += mod_nb

            if lines_nb < categories_nb : # display others when list is truncated
                others_nb = rows_nb - (nb_null + cumul_nb)
                lines.append([f"Others, {categories_nb-lines_nb} modalitie(s)", others_nb, fmt_pc.format(100.*others_nb/rows_nb)])

            if nb_null > 0 :
                lines.append(["Nulls", nb_null, fmt_pc.format(100.*nb_null/rows_nb)])

            print (tabulate (lines,
                             headers = ["Modalities", "Count", "Prop (%)"],
                             tablefmt = tablefmt))

        icol += 1
        print ()

    ######################################################################
    #  Duplicated search
    #  Search and counting is done with duplicated().sum()
    #  Search is done in the DataFrame and DataFrame with ech column droped
    ######################################################################

    print ("=====================================")
    print ()
    print ("Duplicated search")
    print ("With all columns : ", df[df.duplicated()].shape[0])

    if index != None :
        indexes = index.split(",")
        df1 = df.drop (indexes, axis=1)
        print ("Without index(es) : ", df1[df1.duplicated()].shape[0])
    else :
        df1 = df

    print()
    # En comptant les doublons en supprimmant chaque colonne
    lines = []
    if index != None :
        indexes = index.split(",")
        df1 = df.drop (indexes, axis=1)
    else :
        indexes = []
        df1 = df

    for col in df1.columns:
        df2 = df1.drop(col, axis=1)
        lines.append([col, str(df2.duplicated().sum())])
    print (tabulate(lines, headers=["Without", "duplicated"]))

    print ("=====================================")
    print ()
    print ("Correlations")
    print ()
    corr = df.corr(numeric_only=True)
    print (tabulate (corr, headers = corr.columns))

    return

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='df_report: statistiques exploratoires pour aborder un jeu de données.')
    parser.add_argument('filename')                    # positional argument
    parser.add_argument('-s', '--sep',     default = ';')  # option that takes a value
    parser.add_argument('--target',        default = None)
    parser.add_argument('--index',         default = None)
    parser.add_argument('--max_list_len',  default = 10)
    parser.add_argument('--encoding',      default = 'utf-8')
    parser.add_argument('-v', '--verbose', action='store_true')
    args = vars(parser.parse_args())

    filename     = args["filename"]
    sep          = args["sep"]
    encoding     = args["encoding"]
    max_list_len = int(args["max_list_len"])
    index        = args["index"]
    target       = args["target"]

    print ("---->", args["index"])

    df_report(filename,
              sep          = sep,
              encoding     = encoding,
              max_list_len = max_list_len,
              index        = index,
              target       = target)

    sys.exit()
