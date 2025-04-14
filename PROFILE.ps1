Set-Alias dwl '$HOME\Videos\2024_videoDwl\'
function film {
    Set-Location dwl
    git pull
    Set-Location '$HOME\Videos'
    python dwl'fluxvideo.py'
}