#include "ternarydecomposer.h"
#include "stdafx.h"
#include <QtWidgets/QApplication>

int main(int argc, char *argv[]) {

    // Start qt stuff

    QApplication a(argc, argv);

    ternarydecomposer w;
    w.resize(350,150);
    w.setWindowTitle("Ternary Decomposer");

    w.show();
    return a.exec();
}
