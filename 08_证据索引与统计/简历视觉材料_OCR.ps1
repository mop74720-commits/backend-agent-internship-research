$OutputEncoding = [Console]::OutputEncoding = [Text.UTF8Encoding]::new($false)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Runtime.WindowsRuntime
$null = [Windows.Storage.Streams.InMemoryRandomAccessStream, Windows.Storage.Streams, ContentType=WindowsRuntime]
$null = [Windows.Storage.Streams.DataWriter, Windows.Storage.Streams, ContentType=WindowsRuntime]
$null = [Windows.Graphics.Imaging.BitmapDecoder, Windows.Graphics.Imaging, ContentType=WindowsRuntime]
$null = [Windows.Graphics.Imaging.SoftwareBitmap, Windows.Graphics.Imaging, ContentType=WindowsRuntime]
$null = [Windows.Media.Ocr.OcrEngine, Windows.Foundation, ContentType=WindowsRuntime]
$null = [Windows.Media.Ocr.OcrResult, Windows.Foundation, ContentType=WindowsRuntime]
$taskMethod = [System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object { $_.Name -eq 'AsTask' -and $_.IsGenericMethod -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' } | Select-Object -First 1
function Await-Task($Operation, $ResultType) {
    $task = $taskMethod.MakeGenericMethod($ResultType).Invoke($null, @($Operation))
    $task.Wait()
    return $task.Result
}
$inputObject = [Console]::In.ReadToEnd() | ConvertFrom-Json
$imageBytes = [Convert]::FromBase64String($inputObject.image_b64)
$memoryStream = New-Object Windows.Storage.Streams.InMemoryRandomAccessStream
$writer = New-Object Windows.Storage.Streams.DataWriter($memoryStream.GetOutputStreamAt(0))
$writer.WriteBytes($imageBytes)
$null = Await-Task ($writer.StoreAsync()) ([UInt32])
$memoryStream.Seek(0)
$decoder = Await-Task ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($memoryStream)) ([Windows.Graphics.Imaging.BitmapDecoder])
$bitmap = Await-Task ($decoder.GetSoftwareBitmapAsync()) ([Windows.Graphics.Imaging.SoftwareBitmap])
$engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromUserProfileLanguages()
$result = Await-Task ($engine.RecognizeAsync($bitmap)) ([Windows.Media.Ocr.OcrResult])
$safeLines = @()
$maskRects = @()
foreach ($line in $result.Lines) {
    $text = $line.Text
    $rects = @($line.Words | ForEach-Object { $_.BoundingRect })
    if ($rects.Count -eq 0) { continue }
    $x = ($rects.X | Measure-Object -Minimum).Minimum
    $y = ($rects.Y | Measure-Object -Minimum).Minimum
    $right = ($rects | ForEach-Object { $_.X + $_.Width } | Measure-Object -Maximum).Maximum
    $bottom = ($rects | ForEach-Object { $_.Y + $_.Height } | Measure-Object -Maximum).Maximum
    $sensitive = $text -match '(?i)@|(?:\d[\s-]*){7,}|微信|电话|手机|联系|邮箱|住址|地址|QQ|WeChat|Tel\b|E-?mail|phone|https?\s*:|www\.|github\.com|gitee\.com|linkedin|[a-z0-9_-]+\.(?:com|cn|net|org|io|dev)\b'
    if ($sensitive) {
        $maskRects += @{ x=$x; y=$y; width=($right-$x); height=($bottom-$y); reason='contact_or_url_line' }
    } else {
        $safeLines += @{ text=$text; x=$x; y=$y; width=($right-$x); height=($bottom-$y) }
    }
}
@{ width=$bitmap.PixelWidth; height=$bitmap.PixelHeight; safe_lines=$safeLines; mask_rects=$maskRects; engine='Windows.Media.Ocr zh-Hans-CN'; raw_text_saved=$false } | ConvertTo-Json -Depth 7 -Compress
$bitmap.Dispose()
$writer.Dispose()
$memoryStream.Dispose()
