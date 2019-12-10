#include "feudwindow.h"
#include <QApplication>

int main(int argc, char *argv[])
{
    QApplication a(argc, argv);
    FeudWindow w;
    w.show();

    return a.exec();
}
