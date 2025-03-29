# Google Maps API エラー対応ガイド

## 1. 描画ツールが表示されない問題

### エラーの内容
- 地図は表示されるが、描画ツールが表示されない
- コンソールにエラーは表示されない

### 対応方法
1. `DrawingManager`の設定を確認
   - `drawingControl: true`が設定されているか
   - `drawingControlOptions`に正しい位置と描画モードが指定されているか
2. マップの読み込み状態を確認
   - マップが完全に読み込まれた後に`DrawingManager`を表示する
3. 描画モードを明示的に設定
   - `onDrawingManagerLoad`で`setDrawingMode`を呼び出す

```jsx
const onDrawingManagerLoad = (drawingManager) => {
  drawingManager.setDrawingMode(google.maps.drawing.OverlayType.POLYGON);
};
```

## 2. サーバーサイドレンダリング時のエラー

### エラーの内容
- `ReferenceError: window is not defined`
- Next.jsのサーバーサイドレンダリング時に発生

### 対応方法
1. `window`オブジェクトの使用を避ける
   - `window`への直接参照を削除
2. クライアントサイドでのみ実行される処理を`useEffect`内に移動

```jsx
useEffect(() => {
  if (typeof window !== 'undefined' && window.google && google.maps) {
    // クライアントサイドでのみ実行される処理
  }
}, []);
```

## 3. 型エラー

### エラーの内容
- `Type 'string[]' is not assignable to type 'OverlayType[]'`

### 対応方法
1. Google Maps APIの正しい型を使用
   - `google.maps.drawing.OverlayType.POLYGON`を使用

```jsx
const drawingOptions = {
  drawingControlOptions: {
    drawingModes: [google.maps.drawing.OverlayType.POLYGON]
  }
};
```

## 4. デバッグのポイント

- マップの読み込み状態をログ出力
- 描画マネージャーの読み込み状態をログ出力
- コンソールエラーを詳細に確認

```jsx
console.log('Map loaded:', mapLoaded);
console.log('Drawing manager loaded:', drawingManager);
```

## 5. 参考リンク

- [Google Maps JavaScript API Documentation](https://developers.google.com/maps/documentation/javascript/overview)
- [Next.js Server-side Rendering Documentation](https://nextjs.org/docs/pages/building-your-application/rendering/server-side-rendering)
