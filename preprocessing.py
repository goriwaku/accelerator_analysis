import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
import warnings

warnings.filterwarnings('ignore')


def strip_df(df, cols):
    # excelセル内の表記ゆれを修正
    if not cols:
        cols = df.columns
    for col in cols:
        df[col] = df[col].str.strip()
        df[col] = df[col].str.replace(' ', '')
    return df


def process_split_day(df1, df2):
    # 設立から参加までの平均日数を計算
    acc_ls = ['company', 'accelerator', 'participation_date', 'foundation']
    df1 = df1[acc_ls]
    merged_df = pd.merge(df1, df2, on='company')
    ls = []
    del_ls = []
    for item in merged_df.iterrows():
        item = item[1]
        if item['accelerator'] == 1:
            acc_date = pd.to_datetime(item['participation_date'])
            found_date = pd.to_datetime(item['foundation'])
            timedelta = acc_date - found_date
            if (not isinstance(timedelta.days, int)) or timedelta.days <= 0:
                del_ls.append(item['company'])
            else:
                ls.append(timedelta.days)
    mean_days = int(sum(ls)/len(ls))

    # 非参加企業に日付を追加
    split_day = []
    for item in merged_df.iterrows():
        item = item[1]
        if item['accelerator'] == 1:
            split_day.append(pd.to_datetime(item['participation_date']))
        else:
            foundation_date = pd.to_datetime(item['foundation'])
            split_day.append(foundation_date + datetime.timedelta(days=mean_days))
    merged_df['split_day'] = split_day
    for d in del_ls:
        merged_df.drop(merged_df.index[merged_df['company']==d], inplace=True)
    return merged_df


def calc_procurement(df):
    # 参加前、参加後調達額を計算
    df['event_num'] = df['event_num'].fillna(0)
    before_ls = []
    after_ls = []
    non_event_col = ['company', 'accelerator', 'participation_date', 'foundation', 'No.', 'split_day', 'event_num']
    event_df = df.drop(non_event_col, axis=1).T
    event_df.columns = df['company']
    for item in df['company']:
        count = 0
        com_df = df[df['company']==item]
        event_num = com_df['event_num'].values[0]
        split_day = com_df['split_day'].values[0]
        events = list(event_df[item])
        procurement_before = 0
        procurement_after = 0
        while count < event_num:
            day = pd.to_datetime(events.pop(0))
            event_type = events.pop(0)
            series = events.pop(0)
            stock = events.pop(0)
            procurement = events.pop(0)
            valuation = events.pop(0)
            if np.isnan(stock):
                stock = 0
            if np.isnan(procurement):
                procurement = 0
            if np.isnan(valuation):
                valuation = 0
            if (split_day - day).days > 0:
                procurement_before += procurement
            elif (split_day - day).days > -365:
                procurement_after += procurement
            count += 1
        before_ls.append(procurement_before)
        after_ls.append(procurement_after)
    df['procurement_before'] = before_ls
    df['procurement_after'] = after_ls
    return df[['company', 'procurement_after', 'procurement_before']]


def process_split_day_2(df1, df2, obs_term=365):
    df1 = df1[~(df1['accelerator']==1&df1['participation_date'].isna())]
    acc_ls = ['company', 'participation_date', 'foundation']
    df1 = df1[acc_ls]
    df1 = pd.merge(df1, df2, on='company')
    df1['timedelta'] = pd.to_datetime(df1['participation_date']) - pd.to_datetime(df1['foundation'])
    df1['timedelta'] = df1['timedelta'].astype(str).str.replace(' days', '')
    df1.loc[df1['timedelta']=='NaT', 'timedelta'] = '-1'
    df1['timedelta'] = df1['timedelta'].astype(int)
    df1['acc_short'] = (0 <= df1['timedelta'])
    df1.loc[df1['timedelta'] >= obs_term, 'acc_short'] = False
    del_ls = df1[df1['timedelta']<-1]['company']
    df1[df1['timedelta']<0]['timedelta'] = None
    df1['acc_short'].astype(int)
    split_day = []
    for item in df1.iterrows():
        item = item[1]
        if item['acc_short'] == 1:
            split_day.append(pd.to_datetime(item['participation_date']))
            pd.to_datetime(item['participation_date'])
        else:
            foundation_date = pd.to_datetime(item['foundation'])
            split_day.append(foundation_date + datetime.timedelta(days=obs_term//2))
    df1['split_day'] = split_day
    for d in del_ls:
        df1.drop(df1.index[df1['company']==d], inplace=True)
    return df1  


def calc_procurement_2(df, obs_term=365):
    df['event_num'] = df['event_num'].fillna(0)
    before_ls = []
    after_ls = []
    non_event_col = ['company', 'participation_date', 'foundation', 'No.', 'event_num', 'acc_short']
    event_df = df.drop(non_event_col, axis=1).T
    event_df.columns = df['company']
    for item in df['company']:
        count = 0
        com_df = df[df['company']==item]
        event_num = com_df['event_num'].values[0]
        split_day = com_df['split_day'].values[0]
        end_day = pd.to_datetime(com_df['foundation'].values[0]) + datetime.timedelta(days=obs_term)
        events = list(event_df[item])
        procurement_before = 0
        procurement_after = 0
        while count < event_num:
            day = pd.to_datetime(events.pop(0))
            event_type = events.pop(0)
            series = events.pop(0)
            stock = events.pop(0)
            procurement = events.pop(0)
            valuation = events.pop(0)
            if (end_day - day).days < 0:
                break 
            if np.isnan(stock):
                stock = 0
            if np.isnan(procurement):
                procurement = 0
            if np.isnan(valuation):
                valuation = 0
            if (split_day - day).days > 0:
                procurement_before += procurement
            elif (split_day - day).days > -365:
                procurement_after += procurement
            count += 1
        before_ls.append(procurement_before)
        after_ls.append(procurement_after)
    df['procurement_before'] = before_ls
    df['procurement_after'] = after_ls
    return df[['company', 'procurement_after', 'procurement_before', 'acc_short']]


def create_industry_dummies(df):
    energy_semiconductor = []
    finance = []
    ecology = []
    bio = []
    computer = []
    service = []
    for item in df['company']:
        industry = df[df['company']==item]['industry'].values[0]
        if industry in ['半導体/その他電子部品・製品', '産業・エネルギー ICT', '産業・エネルギー', '産業・エネルギーICT']:
            energy_semiconductor.append(1)
            finance.append(0)
            ecology.append(0)
            bio.append(0)
            computer.append(0)
            service.append(0)
        elif industry in ['金融・保険・不動産 ICT', '金融・保険・不動産', '金融・保険・不動産ICT']:
            energy_semiconductor.append(0)
            finance.append(1)
            ecology.append(0)
            bio.append(0)
            computer.append(0)
            service.append(0)
        elif industry in ['環境関連', '環境関連ICT', '環境関連 ICT']:
            energy_semiconductor.append(0)
            finance.append(0)
            ecology.append(1)
            bio.append(0)
            computer.append(0)
            service.append(0)
        elif industry in ['医療・ヘルスケアICT', '医療・ヘルスケア ICT',  '医療・ヘルスケア', 'バイオテクノロジー']:
            energy_semiconductor.append(0)
            finance.append(0)
            ecology.append(0)
            bio.append(1)
            computer.append(0)
            service.append(0)
        elif industry in ['消費者向けサービス・販売', 'ビジネスサービス']:
            energy_semiconductor.append(0)
            finance.append(0)
            ecology.append(0)
            bio.append(0)
            computer.append(0)
            service.append(1)
        else:
            energy_semiconductor.append(0)
            finance.append(0)
            ecology.append(0)
            bio.append(0)
            computer.append(1)
            service.append(0)
    df['energy_and_semiconductor'] = energy_semiconductor
    df['finance'] = finance
    df['ecology'] = ecology
    df['bio'] = bio
    df['computer'] = computer
    df['service'] = service
    return df.drop('industry', axis=1)


def make_dataset_for_reg(df, df_acc):
    df_acc = df_acc.drop(['accelerator', 'accelerator_name'], axis=1)
    df = pd.merge(df, df_acc, on='company', how='inner')
    df_non_acc = df[df['accelerator']==0]
    df = df[df['accelerator']==1]

    # 参加までの日数を追加
    df['timedelta'] = pd.to_datetime(df['participation_date']) - pd.to_datetime(df['foundation'])
    df['timedelta'] = df['timedelta'].dt.days

    # アクセラの種類ダミーを追加
    df = add_accelerator_type(df)

    # 必要な列のみcsvに
    needed_cols = ['capital', 'university', 'venture', 'enterprise', 'procurement_before', 'procurement_after','timedelta', 
                  'accelerator_type', 'energy_and_semiconductor', 'finance', 'ecology','bio', 'computer', 'service', 'accelerator']

    df = df[needed_cols]
    df.drop('accelerator', axis=1).to_csv('dataset/dataset_for_regression.csv', index=False)

    # アクセラ参加日による分割データセットの作成
    mean_timedelta = df['timedelta'].mean()
    over_mean = df[df['timedelta'] > mean_timedelta] 
    less_mean = df[df['timedelta'] <= mean_timedelta]
    needed_cols = ['capital', 'university', 'venture', 'enterprise', 'procurement_before', 'procurement_after',
                   'energy_and_semiconductor', 'finance', 'ecology','bio', 'computer', 'service', 'accelerator']
    pd.concat([df_non_acc, over_mean], axis=0)[needed_cols].dropna().to_csv('dataset/over_mean.csv', index=False)
    pd.concat([df_non_acc, less_mean], axis=0)[needed_cols].dropna().to_csv('dataset/less_mean.csv', index=False)


def add_accelerator_type(df):
    acc_type_ls = []
    for item in df['governing'].values:
        if item == '公共機関':
            acc_type_ls.append(0)
        elif item == '企業':
            acc_type_ls.append(1)
        else:
            acc_type_ls.append(np.nan)
    df['accelerator_type'] = acc_type_ls
    return df



def main():
    # データの読み込み
    main_df = pd.read_excel('raw_data/傾向スコアマッチング対象企業.xlsx')
    new_df = pd.read_excel('raw_data/INITIAL追加データ_ラウンド情報_Final.xlsx')
    acc_df = pd.read_excel('raw_data/924運営母体.xlsx')
    main_df.columns = ['No.', 'company', 'foundation', 'industry', 'capital', 'university', 'univ_name', 'venture', 'enterprise', 
                       'accelerator', 'accelerator_name', 'participation_date', 'procurement', 'close', 'close_date', 'close_type']
    new_df.columns = ['No.', 'company', 'event_num'] + list(new_df.columns[3:])
    acc_df.columns = ['No.', 'company', 'accelerator', 'accelerator_name', 'governing']
    main_df = strip_df(main_df, cols=('company', 'industry'))
    fill_0_cols = ['accelerator', 'university', 'venture', 'enterprise']
    main_df[fill_0_cols] = main_df[fill_0_cols].fillna(0)
    new_df = strip_df(new_df, cols=('company', ))
    acc_df = strip_df(acc_df, cols=('company', ))

    # 調達額の計算
    proc_df = process_split_day(main_df, new_df)
    proc_df = calc_procurement(proc_df)
    proc_df_2 = process_split_day_2(main_df, new_df, obs_term=365)
    proc_df_2 = calc_procurement_2(proc_df_2, obs_term=365)
    merged_df = pd.merge(main_df, proc_df, how='inner', on='company')
    merged_df_2 = pd.merge(main_df, proc_df_2, how='inner', on='company')

    # 廃業企業の削除
    merged_df = merged_df[merged_df['close']!=1]
    merged_df_2 = merged_df_2[merged_df_2['close']!=1]

    # 業界ダミーの作成
    merged_df = create_industry_dummies(merged_df)
    merged_df_2 = create_industry_dummies(merged_df_2)

    # アクセラ参加企業の回帰分析用データ作成
    make_dataset_for_reg(merged_df, acc_df)

    # 傾向スコアマッチング用のデータを作成
    needed_cols = ['capital', 'university', 'venture', 'enterprise', 'accelerator', 'procurement_before', 
                   'procurement_after', 'energy_and_semiconductor', 'finance', 'ecology', 'bio', 'computer', 'service']
    merged_df = merged_df[needed_cols]
    merged_df.to_csv('dataset/df_with_na.csv', index=False)
    merged_df2 = merged_df.fillna(0)
    merged_df2.to_csv('dataset/df_filled_na.csv', index=False)
    merged_df = merged_df.dropna()
    merged_df.to_csv('dataset/df_dropped_na.csv', index=False)

    # 観察期間制限のデータ
    needed_cols = ['capital', 'university', 'venture', 'enterprise', 'procurement_before', 'acc_short',
                   'procurement_after', 'energy_and_semiconductor', 'finance', 'ecology', 'bio', 'computer', 'service']
    merged_df_2 = merged_df_2[needed_cols]
    merged_df_2 = merged_df_2.dropna()
    merged_df_2.to_csv('dataset/df_ltd.csv', index=False)


if __name__ == '__main__':
    main()