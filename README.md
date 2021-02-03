# lapanalysis.py
レース分析.txtにラップ分析したいレースのnetkeibaの出馬表のURLを一番上に貼る。(https://race.netkeiba.com/race/shutuba.html?race_id={race_id})
そこから下は平均を出すために使うレースのnetkeibaのレース結果のURLを貼る。(https://db.netkeiba.com/race/{race_id})
レース分析.txtが準備できたら以下コマンドで実行する。
```
python lapanalysis.py
```

# courseanalysis.py
コース分析.txtにフォルダ名を一番上に、コース分析したいレースの距離を上から2番目に記入する。
そこから下は平均を出すために使うレースのnetkeibaのレース結果のURLを貼る。(https://db.netkeiba.com/race/{race_id})
コース分析.txtが準備できたら以下コマンドで実行する。
```
python courseanalysis.py
```

# getraceresult.py
指定した日のレース結果を取得する。
以下コマンドで実行する。
```
python getraceresult.py {race_idのレース数の部分を除いたもの}
```