/*
    Copyright 2016 - 2021 Benjamin Vedder	benjamin@vedder.se

    This file is part of VESC Tool.

    VESC Tool is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    VESC Tool is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
    */

#include "pagefoc.h"
#include "ui_pagefoc.h"
#include <QMessageBox>

PageFoc::PageFoc(QWidget *parent) :
    QWidget(parent),
    ui(new Ui::PageFoc)
{
    ui->setupUi(this);
    layout()->setContentsMargins(0, 0, 0, 0);
    mVesc = nullptr;
}

PageFoc::~PageFoc()
{
    delete ui;
}

VescInterface *PageFoc::vesc() const
{
    return mVesc;
}

void PageFoc::setVesc(VescInterface *vesc)
{
    mVesc = vesc;

    if (mVesc) {
        ui->detectFoc->setVesc(mVesc);
        ui->detectFocHall->setVesc(mVesc);
        ui->detectFocEncoder->setVesc(mVesc);

        reloadParams();
    }
}

void PageFoc::reloadParams()
{
    if (mVesc) {
        ui->generalTab->clearParams();
        ui->sensorlessTab->clearParams();
        ui->hallTab->clearParams();
        ui->encoderTab->clearParams();
        ui->hfiTab->clearParams();
        ui->vssTab->clearParams();
        ui->filterTab->clearParams();
        ui->offsetTab->clearParams();
        ui->fwTab->clearParams();
        ui->advancedTab->clearParams();

        ui->generalTab->addParamSubgroup(mVesc->mcConfig(), "foc", tr("通用"));
        ui->sensorlessTab->addParamSubgroup(mVesc->mcConfig(), "foc", tr("无感"));
        ui->hallTab->addParamSubgroup(mVesc->mcConfig(), "foc", tr("霍尔传感器"));
        ui->encoderTab->addParamSubgroup(mVesc->mcConfig(), "foc", tr("编码器"));
        ui->hfiTab->addParamSubgroup(mVesc->mcConfig(), "foc", "hfi");
        ui->vssTab->addParamSubgroup(mVesc->mcConfig(), "foc", "vss");
        ui->filterTab->addParamSubgroup(mVesc->mcConfig(), "foc", tr("滤波器"));
        ui->offsetTab->addParamSubgroup(mVesc->mcConfig(), "foc", tr("偏移"));
        ui->fwTab->addParamSubgroup(mVesc->mcConfig(), "foc", tr("弱磁"));
        ui->advancedTab->addParamSubgroup(mVesc->mcConfig(), "foc", tr("高级"));
    }
}

void PageFoc::on_openloopOldButton_clicked()
{
    if (mVesc) {
        mVesc->mcConfig()->updateParamDouble("foc_openloop_rpm", 700.0);
        mVesc->mcConfig()->updateParamDouble("foc_openloop_rpm_low", 0.0);
        mVesc->mcConfig()->updateParamDouble("foc_sl_openloop_hyst", 0.1);
        mVesc->mcConfig()->updateParamDouble("foc_sl_openloop_time", 0.1);
        mVesc->mcConfig()->updateParamDouble("foc_sl_openloop_time_lock", 0.0);
        mVesc->mcConfig()->updateParamDouble("foc_sl_openloop_time_ramp", 0.0);
    }
}

void PageFoc::on_openloopGenericButton_clicked()
{
    mVesc->mcConfig()->updateParamDouble("foc_openloop_rpm", 1200.0);
    mVesc->mcConfig()->updateParamDouble("foc_openloop_rpm_low", 0.1);
    mVesc->mcConfig()->updateParamDouble("foc_sl_openloop_hyst", 0.1);
    mVesc->mcConfig()->updateParamDouble("foc_sl_openloop_time", 0.05);
    mVesc->mcConfig()->updateParamDouble("foc_sl_openloop_time_lock", 0.0);
    mVesc->mcConfig()->updateParamDouble("foc_sl_openloop_time_ramp", 0.1);
}

void PageFoc::on_openloopFastStartButton_clicked()
{
    mVesc->mcConfig()->updateParamDouble("foc_openloop_rpm", 1500.0);
    mVesc->mcConfig()->updateParamDouble("foc_openloop_rpm_low", 0.0);
    mVesc->mcConfig()->updateParamDouble("foc_sl_openloop_hyst", 0.1);
    mVesc->mcConfig()->updateParamDouble("foc_sl_openloop_time", 0.1);
    mVesc->mcConfig()->updateParamDouble("foc_sl_openloop_time_lock", 0.0);
    mVesc->mcConfig()->updateParamDouble("foc_sl_openloop_time_ramp", 0.0);
}

void PageFoc::on_openloopPropellerButton_clicked()
{
    mVesc->mcConfig()->updateParamDouble("foc_openloop_rpm", 1500.0);
    mVesc->mcConfig()->updateParamDouble("foc_openloop_rpm_low", 0.1);
    mVesc->mcConfig()->updateParamDouble("foc_sl_openloop_hyst", 0.1);
    mVesc->mcConfig()->updateParamDouble("foc_sl_openloop_time", 0.1);
    mVesc->mcConfig()->updateParamDouble("foc_sl_openloop_time_lock", 0.1);
    mVesc->mcConfig()->updateParamDouble("foc_sl_openloop_time_ramp", 0.1);
}

void PageFoc::on_openloopHeavyInertialButton_clicked()
{
    mVesc->mcConfig()->updateParamDouble("foc_openloop_rpm", 1500.0);
    mVesc->mcConfig()->updateParamDouble("foc_openloop_rpm_low", 0.1);
    mVesc->mcConfig()->updateParamDouble("foc_sl_openloop_hyst", 0.1);
    mVesc->mcConfig()->updateParamDouble("foc_sl_openloop_time", 0.2);
    mVesc->mcConfig()->updateParamDouble("foc_sl_openloop_time_lock", 0.5);
    mVesc->mcConfig()->updateParamDouble("foc_sl_openloop_time_ramp", 0.5);
}

void PageFoc::on_offsetMeasureButton_clicked()
{
    if (mVesc) {
        if (!mVesc->isPortConnected()) {
            QMessageBox::critical(this,
                                         tr("连接错误"),
                                         tr("VESC 未连接。请先连接。"));
            return;
        }

        QMessageBox::StandardButton reply;
        reply = QMessageBox::information(this,
                                         tr("测量偏移"),
                                         tr("这将测量并存储所有偏移。请确保电机未转动或已断开连接。"
                                            "测量期间电机旋转将导致无效结果。是否继续？"),
                                         QMessageBox::Yes | QMessageBox::No, QMessageBox::Yes);

        if (reply == QMessageBox::Yes) {
            ui->offsetMeasureButton->setEnabled(false);
            mVesc->commands()->sendTerminalCmd("foc_dc_cal");
            QTimer::singleShot(5000, [this]() {
                mVesc->commands()->getMcconf();
                ui->offsetMeasureButton->setEnabled(true);
            });
        }
    }
}
