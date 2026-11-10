set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
chmod +x "$DIR/launch.sh"

ICON_DEST="$HOME/.local/share/icons/hicolor/128x128/apps"
APP_DEST="$HOME/.local/share/applications"

mkdir -p "$ICON_DEST" "$APP_DEST"

# Install icon, can be changed to your liking
if [ -f "$DIR/assets/icon.png" ]; then
    cp "$DIR/assets/icon.png" "$ICON_DEST/acdc.png"
fi

cat <<EOF > "$APP_DEST/acdc.desktop"
[Desktop Entry]
Version=1.0
Type=Application
Name=Animal Crossing Dynamic Clock
GenericName=Dynamic Music Player
Comment=Cozy Animal Crossing soundtrack synced to your local time and weather
Exec="$DIR/launch.sh"
Path=$DIR
Icon=acdc
Terminal=false
Categories=AudioVideo;Audio;Player;
Keywords=animal;crossing;music;clock;weather;ost;
StartupNotify=false
X-GNOME-Autostart-enabled=true
EOF

chmod +x "$APP_DEST/acdc.desktop"

if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$APP_DEST" >/dev/null 2>&1 || true
fi

echo "Animal Crossing Dynamic Clock installed successfully!"
echo "You can now launch it from your application menu or by running ./launch.sh"
