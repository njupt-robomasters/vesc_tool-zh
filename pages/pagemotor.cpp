/*
    Copyright 2016 - 2017 Benjamin Vedder	benjamin@vedder.se

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

#include "pagemotor.h"
#include "ui_pagemotor.h"

PageMotor::PageMotor(QWidget *parent) :
    QWidget(parent),
    ui(new Ui::PageMotor)
{
    ui->setupUi(this);
    layout()->setContentsMargins(0, 0, 0, 0);
    mVesc = nullptr;
}

PageMotor::~PageMotor()
{
    delete ui;
}

VescInterface *PageMotor::vesc() const
{
    return mVesc;
}

void PageMotor::setVesc(VescInterface *vesc)
{
    mVesc = vesc;

    if (mVesc) {
        ui->dirSetup->setVesc(mVesc);
        ui->batteryCalc->setVesc(mVesc);

        reloadParams();
    }
}

void PageMotor::reloadParams()
{
    ui->motorTab->clearParams();
    ui->sensorsTab->clearParams();
    ui->currentTab->clearParams();
    ui->voltageTab->clearParams();
    ui->rpmTab->clearParams();
    ui->wattageTab->clearParams();
    ui->tempTab->clearParams();
    ui->bmsTab->clearParams();
    ui->advancedTab->clearParams();

    ui->motorTab->addParamSubgroup(mVesc->mcConfig(), "通用", tr("通用"));
    ui->sensorsTab->addParamSubgroup(mVesc->mcConfig(), "通用", tr("传感器"));
    ui->currentTab->addParamSubgroup(mVesc->mcConfig(), "通用", tr("电流"));
    ui->voltageTab->addParamSubgroup(mVesc->mcConfig(), "通用", tr("电压"));
        ui->rpmTab->addParamSubgroup(mVesc->mcConfig(), "通用", "RPM");
    ui->wattageTab->addParamSubgroup(mVesc->mcConfig(), "通用", tr("功率"));
    ui->tempTab->addParamSubgroup(mVesc->mcConfig(), "通用", tr("温度"));
        ui->bmsTab->addParamSubgroup(mVesc->mcConfig(), "通用", "BMS");
    ui->advancedTab->addParamSubgroup(mVesc->mcConfig(), "通用", tr("高级"));
}
