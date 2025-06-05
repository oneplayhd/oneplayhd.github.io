import sys
import xbmcplugin
import xbmcgui
import xbmcaddon
import xbmc

# Configurações do addon
addon = xbmcaddon.Addon()
addon_handle = int(sys.argv[1])

# URL do fluxo M3U8
m3u8_url = 'https://wplaycine.top/play/UhqJtC401yt6xD8YovnHfmP-urBgi7SXrdWcuWYaqNURq8tKGb1gjsuEo2VxLoW5'  # Substitua com o URL do seu fluxo

# Menu principal do addon
def main_menu():
    # Cria um item de lista para o vídeo
    li = xbmcgui.ListItem('Play Stream')
    li.setInfo('video', {'title': 'Stream Title', 'genre': 'Live'})
    li.setArt({'icon': 'DefaultVideo.png'})
    
    # Adiciona o item à interface do Kodi
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=m3u8_url, listitem=li)
    
    # Finaliza a adição de itens
    xbmcplugin.endOfDirectory(addon_handle)

# Reproduz o fluxo se for selecionado
def play_stream(url):
    li = xbmcgui.ListItem(path=url)
    xbmcplugin.setResolvedUrl(addon_handle, True, listitem=li)

# Verifica a ação a ser tomada
if __name__ == '__main__':
    # Se um URL foi passado, reproduz o stream, senão exibe o menu
    if len(sys.argv) > 2 and sys.argv[2].startswith('?'):
        play_stream(m3u8_url)
    else:
        main_menu()
