#include <QCoreApplication>
#include <QDebug>
#include "vescinterface.h"

int main(int argc, char *argv[]) {
    QCoreApplication app(argc, argv);
    VescInterface vesc;
    
    vesc.mcConfig()->loadParamsXml("res/config/7.00/parameters_mcconf.xml");
    
    QTextStream out(stdout);
    out << "=== Groups ===" << Qt::endl;
    auto groups = vesc.mcConfig()->getParamGroups();
    for (auto g : groups) {
        out << "Group: " << g << " (hex: " << g.toUtf8().toHex() << ")" << Qt::endl;
        auto subgroups = vesc.mcConfig()->getParamSubgroups(g);
        for (auto s : subgroups) {
            auto params = vesc.mcConfig()->getParamsFromSubgroup(g, s);
            out << "  Sub: " << s << " (hex: " << s.toUtf8().toHex() << ") -> " << params.size() << " params" << Qt::endl;
            if (params.isEmpty()) {
                out << "    *** EMPTY! Group matching may fail! ***" << Qt::endl;
            }
        }
    }
    return 0;
}
