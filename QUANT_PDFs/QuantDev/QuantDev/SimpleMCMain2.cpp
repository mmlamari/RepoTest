/*
requires
PayOff1.cpp
Random1.cpp,
SimpleMC.cpp,
*/
#include "stdafx.h"
#include"SimpleMC.h"
#include<iostream>
using namespace std;


int main()
{
double Expiry;
double Strike;
double Spot;
double Vol;
double r;
unsigned long NumberOfPaths;
cout << "\nEnter expiry\n";
cin >> Expiry;
cout << "\nEnter strike\n";
cin >> Strike;
cout << "\nEnter spot\n";
cin >> Spot;
cout << "\nEnter vol\n";
cin >> Vol;
cout << "\nr\n";
cin >> r;
cout << "\nNumber of paths\n";
cin >> NumberOfPaths;
PayOff callPayOff(Strike, PayOff::call);
PayOff putPayOff(Strike, PayOff::put);
PayOff digitalcallPayOff(Strike, PayOff::digitalcall);
double resultCall = SimpleMonteCarlo2(callPayOff,
Expiry,
Spot,
Vol,
r,
NumberOfPaths);
double resultPut = SimpleMonteCarlo2(putPayOff,
Expiry,
Spot,
Vol,
r,
NumberOfPaths);

double resultDigitalcall = SimpleMonteCarlo2(digitalcallPayOff,
Expiry,
Spot,
Vol,
r,
NumberOfPaths);
cout <<"the prices are " << resultCall
<< " for the call and "
<< resultPut
<< " for the put\n"
<< resultDigitalcall
<< " for the digitalcall\n";
double tmp;
cin >> tmp;
return 0;
}