#ifndef FEUDWINDOW_H
#define FEUDWINDOW_H

#include <QMainWindow>

namespace Ui {
class FeudWindow;
}

class FeudWindow : public QMainWindow
{
    Q_OBJECT

public:
    explicit FeudWindow(QWidget *parent = 0);
    ~FeudWindow();

private:
    Ui::FeudWindow *ui;
};

#endif // FEUDWINDOW_H
