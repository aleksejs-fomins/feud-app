#include "feudwindow.h"
#include "ui_feudwindow.h"

FeudWindow::FeudWindow(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::FeudWindow)
{
    ui->setupUi(this);
}

FeudWindow::~FeudWindow()
{
    delete ui;
}
