




#define WEBVIEW_IMPLEMENTATION
//don't forget to define WEBVIEW_WINAPI,WEBVIEW_GTK or WEBVIEW_COCAO
#define WEBVIEW_WINAPI
#include "webview.h"

char HTML_CODE[] = "document.documentElement.innerHTML = '<!DOCTYPE html> <html> <head> <title>Document</title> </head> <body  style=\"padding: 0px; margin: 0px;width: 100%; height: 100%; background-color: cadetblue;\"> Hello... </body> </html>';"; 


int main(int argc, char *argv[])
{
    struct webview webview;
    memset(&webview, 0, sizeof(webview));
    webview.title = "title";
    webview.url = "";
    webview.width = 500;
    webview.height = 500;
    webview.resizable = FALSE;
    int r = webview_init(&webview);
    if (r != 0) {
        return r;
    }
    webview_eval(&webview, HTML_CODE);
    while (webview_loop(&webview, 1) == 0) {
    }
    webview_exit(&webview);
    return 0;
}
