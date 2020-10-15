#pragma once

#include <QtWidgets/QMainWindow>
#include <QtWidgets/qpushbutton.h>
#include <QtWidgets/qlabel.h>
#include <QtWidgets/qprogressbar.h>
#include <QtWidgets/qcheckbox.h>
#include <QtWidgets/qfiledialog.h>

class ternarydecomposer : public QMainWindow {
    //Q_OBJECT // Commenting this makes everything run smoothly

public:
    ternarydecomposer(QWidget* parent = Q_NULLPTR);

private slots:
    void flBtn_onClick();

private:
    QLabel* lbl;
    QCheckBox* cbox;
    QProgressBar* pBar;
};