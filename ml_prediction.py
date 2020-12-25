import numpy as np
import pandas as pd
import sklearn
import lightgbm as lgbm
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold, train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
import tensorflow as tf


RANDOM_STATE = 0


def main():
    # 欠損値ありのデータを読み込み
    df_all = pd.read_csv('dataset/df_with_na.csv')
    X_col = ['capital', 'university', 'venture', 'enterprise','procurement_before', 'energy_and_semiconductor','finance', 'ecology', 'bio', 'computer']
    y_col = ['accelerator']
    X = df_all[X_col]
    y = df_all[y_col]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y)

    # lgbmによる傾向スコアの構成
    lgbm_model = lgbm.LGBMClassifier(random_state=RANDOM_STATE, 
                                     class_weight={1:5.5, 0:1},  
                                     colsample_bytree=0.8,
                                     learning_rate=0.1,
                                     n_estimators=500,
                                     min_child_weight=30,
                                     )
    lgbm_model.fit(X_train, y_train)
    lgbm_pred = lgbm_model.predict_proba(X)[:, 1]
    df_all['lgbm_pred'] = lgbm_pred
    df_all.to_csv('predicted/df_with_na_with_ml.csv', index=False)

    # 欠損値なしのデータを読み込み
    df_dropped = pd.read_csv('dataset/df_dropped_na.csv')
    X = df_dropped[X_col]
    y = df_dropped[y_col]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y)

    # lgbmによる傾向スコアの構成
    lgbm_model = lgbm.LGBMClassifier(random_state=RANDOM_STATE, 
                                     class_weight={1:5.5, 0:1},  
                                     colsample_bytree=0.8,
                                     learning_rate=0.1,
                                     n_estimators=500,
                                     min_child_weight=30,
                                     )
    lgbm_model.fit(X_train, y_train)
    lgbm_pred = lgbm_model.predict_proba(X)[:, 1]
    df_dropped['lgbm_pred'] = lgbm_pred


    # NNによる傾向スコアの構成
    tf.random.set_seed(RANDOM_STATE)
    scaler = StandardScaler()
    scaler.fit(X[['capital', 'procurement_before']])
    X_train[['capital', 'procurement_before']] = scaler.transform(X_train[['capital', 'procurement_before']])
    X_test[['capital', 'procurement_before']] = scaler.transform(X_test[['capital', 'procurement_before']])
    nn_model = tf.keras.models.Sequential([
        tf.keras.layers.Dense(10, activation='relu', input_shape=(10,), kernel_regularizer=tf.keras.regularizers.l2(1),),
        tf.keras.layers.Dense(10, activation='relu', kernel_regularizer=tf.keras.regularizers.l2(10),),
        tf.keras.layers.Dense(5, activation='relu', kernel_regularizer=tf.keras.regularizers.l2(1),),
        tf.keras.layers.Dense(1, activation='sigmoid')
    ])
    nn_model.compile(
        optimizer='adam',  # Optimizer
        # Loss function to minimize
        loss='binary_crossentropy',
        # List of metrics to monitor
        metrics=['AUC']
    )
    class_weight = {0: 1., 1: 5.5,}
    nn_model.fit(X_train, y_train, epochs=45, class_weight=class_weight)
    nn_pred = pd.DataFrame(nn_model.predict(X)).explode(0)[0]
    df_dropped['nn_pred'] = nn_pred

    df_dropped.to_csv('predicted/df_dropped_na_with_ml.csv', index=False)

    # 分割データセットの傾向スコア構成
    ls = ['over_mean', 'less_mean']
    for itm in ls:
        df = pd.read_csv('dataset/' + itm + '.csv')
        X = df[X_col]
        y = df[y_col].astype(int)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y)

        # lgbmによる傾向スコアの構成
        lgbm_model = lgbm.LGBMClassifier(random_state=RANDOM_STATE, 
                                        class_weight={1:5.5, 0:1},  
                                        colsample_bytree=0.8,
                                        learning_rate=0.1,
                                        n_estimators=500,
                                        min_child_weight=30,
                                        )
        lgbm_model.fit(X_train, y_train)
        lgbm_pred = lgbm_model.predict_proba(X)[:, 1]
        df['lgbm_pred'] = lgbm_pred
        df.to_csv('predicted/' + itm + '_with_ml.csv', index=False)


if __name__ == '__main__':
    main()