#define WriteCommand (0xA0)
#define EndMark (0x20)
#define ReadCommand (0xA1)
#define WriteCommandWord (0xA2)
/////////////////////////////////////////////////////////////////////////////
// CUSBDrive window

class CUSBDrive
{
public:
	BOOL ReadUSBParameter(unsigned char *Parameter);
	UINT DriveID;
	BOOL CheckHandle();
	BOOL ReadData(int Address,LPVOID lpBuff);
	BOOL WriteData(int Address,LPVOID lpBuff);
	BOOL WriteData(int Address,unsigned char Data);
	HANDLE m_HidHandle;
	CUSBDrive();
	virtual ~CUSBDrive();

private:
	HANDLE FindHandle();
	BOOL ReadData(LPVOID lpBuffer);
	BOOL WriteData(LPVOID lpBuffer);
};



CUSBDrive::CUSBDrive()
{
	m_HidHandle=FindHandle();
}

CUSBDrive::~CUSBDrive()
{

}

BOOL CUSBDrive::WriteData(LPVOID lpBuffer)
{
	if(m_HidHandle == INVALID_HANDLE_VALUE)
		{
   /*     //MessageBox("设备未连接");
        return false;
		}

	 char	reportbuf[9];

	::memcpy( &reportbuf[1],lpBuffer,8);
	reportbuf[0]=0;

	OVERLAPPED op={0};
	HANDLE hEvent=CreateEvent(NULL,false,false,NULL);
	op.hEvent=hEvent;

	ULONG	nWritten;
	    
	if(!WriteFile(m_HidHandle, &reportbuf[0],9,&nWritten,  &op))//0))
	{
			DWORD dwErr=::GetLastError();
			//AfxMessageBox("发送erase command失败!");
			if(dwErr != ERROR_IO_PENDING )
			{
				CloseHandle(hEvent);
			    return false;
			}
		    else
			{
		    	DWORD dwObj=WaitForSingleObject(op.hEvent,50);
		    	if(dwObj==WAIT_OBJECT_0)
				{
					CloseHandle(hEvent);
				   return true;
				}
		    	else if(dwObj==WAIT_TIMEOUT)
				{
					CancelIo(m_HidHandle);
				CloseHandle(hEvent);
				return false;
				}
			}
//			return false;
	}
   	//AfxMessageBox("发送erase command ok! 3s后可以写flash");
	CloseHandle(hEvent);
	return true;*/
}

BOOL CUSBDrive::ReadData(LPVOID lpBuffer)
{
	if(m_HidHandle == INVALID_HANDLE_VALUE)
		{
        //MessageBox("设备未连接");
        return false;
		}

	char	reportbuf[9];
	memset(reportbuf,0,9);
//	reportbuf[0]=2;	
	OVERLAPPED op={0};
	HANDLE hEvent=CreateEvent(NULL,false,false,NULL);
	op.hEvent=hEvent;

	ULONG	nWritten;
	    
		 if(!ReadFile(m_HidHandle, &reportbuf[0],9,&nWritten,  &op))//0))
		{
			DWORD dwErr=::GetLastError();
			//AfxMessageBox("发送erase command失败!");
			if(dwErr != ERROR_IO_PENDING )
			{
				CloseHandle(hEvent);
			    return false;
			}
		    else
			{
		    	DWORD dwObj=WaitForSingleObject(op.hEvent,1200);
		    	if(dwObj==WAIT_OBJECT_0)
				{
					
					::memcpy(lpBuffer,&reportbuf[1],8);
					CloseHandle(hEvent);
				   return true;
				}
		    	else if(dwObj==WAIT_TIMEOUT)
				{
					CancelIo(m_HidHandle);
					CloseHandle(hEvent);
				return false;
				}
			}
//			return false;
		}

   	::memcpy(lpBuffer,&reportbuf[1],8);
	
	//AfxMessageBox("发送erase command ok! 3s后可以写flash");
	CloseHandle(hEvent);
	return true;
}

HANDLE CUSBDrive::FindHandle()
{
	HANDLE hidHandle=INVALID_HANDLE_VALUE;

	//查找本系统中HID类的GUID标识
    GUID hidGuid;

    HidD_GetHidGuid(&hidGuid);           

	//准备查找符合HID规范的USB设备,获取HID类设备信息集
    HDEVINFO hDevInfo = SetupDiGetClassDevs(&hidGuid,
                                            NULL,
                                            NULL,
                                            (DIGCF_PRESENT | DIGCF_DEVICEINTERFACE)); 
    if(hDevInfo==INVALID_HANDLE_VALUE)
    {
        //m_Status.SetWindowText("获取HID设备信息失败!");
		hidHandle=INVALID_HANDLE_VALUE;
        return  hidHandle;
    }

    SP_DEVICE_INTERFACE_DATA devInfoData;
    devInfoData.cbSize = sizeof (SP_DEVICE_INTERFACE_DATA);
    int deviceNo = 0;
	BOOL bSuccess=false;

 //   SetLastError(NO_ERROR);

 //   while(GetLastError() != ERROR_NO_MORE_ITEMS)
	
	do
    {
		// 枚举设备接口信息
		bSuccess=SetupDiEnumDeviceInterfaces (hDevInfo,
											  0, 
											  &hidGuid,
										      deviceNo,
											  &devInfoData);
		//找到了可用的USB设备
        if(bSuccess&&(GetLastError()!=ERROR_NO_MORE_ITEMS)) 
        {
			//若找到了一个USB设备，则获取该设备的细节信息
            ULONG  requiredLength = 0;

			PSP_INTERFACE_DEVICE_DETAIL_DATA devDetail;
            SetupDiGetDeviceInterfaceDetail(hDevInfo,
                                            &devInfoData,
                                            NULL, 
                                            0, 
                                            &requiredLength,
                                            NULL);

            devDetail = (PSP_INTERFACE_DEVICE_DETAIL_DATA) malloc (requiredLength);
            devDetail->cbSize = sizeof(SP_INTERFACE_DEVICE_DETAIL_DATA);

            if(! SetupDiGetDeviceInterfaceDetail(hDevInfo,
                                                 &devInfoData,
                                                 devDetail,
                                                 requiredLength,
                                                 NULL,
                                                 NULL)) 
				{
                //AfxMessageBox("获取HID设备细节信息失败!");
                free(devDetail);
				hidHandle=INVALID_HANDLE_VALUE;
                return hidHandle;
				}
			
            hidHandle = CreateFile(devDetail->DevicePath,
                                   GENERIC_READ | GENERIC_WRITE,
                                   FILE_SHARE_READ|FILE_SHARE_WRITE,
                                   NULL, 
								   OPEN_EXISTING,         
                                   FILE_FLAG_OVERLAPPED|FILE_ATTRIBUTE_NORMAL,
			   					  //NULL,
                                  NULL);
		
			DWORD err;
			err=GetLastError();
            free(devDetail);

            if(hidHandle==INVALID_HANDLE_VALUE)
				{
             //   AfxMessageBox("获取HID设备句柄失败!");
				++deviceNo;
                continue;
				}

            HIDD_ATTRIBUTES hidAttributes;
            if(!HidD_GetAttributes(hidHandle, &hidAttributes))
				{
            //    AfxMessageBox("获取HID设备属性失败!");
                CloseHandle(hidHandle);
				hidHandle=INVALID_HANDLE_VALUE;
                return	hidHandle;
				}

            if(USB_VID == hidAttributes.VendorID &&			//USB_VID
               USB_PID  == hidAttributes.ProductID &&			//USB_PID
               USBRS232_VERSION == hidAttributes.VersionNumber)

				{
				SetupDiDestroyDeviceInfoList(hDevInfo);
			    return	hidHandle;
				}
            else
				{
                CloseHandle(hidHandle);
                ++deviceNo;
				}
        }
	else break;//没有找到可用的设备或者没找到更多的可用设备
	}while(bSuccess);

	SetupDiDestroyDeviceInfoList(hDevInfo);
	hidHandle=INVALID_HANDLE_VALUE;
	return hidHandle;
}

BOOL CUSBDrive::WriteData(int Address, unsigned char Data)
{
	unsigned char buf[8];
	buf[0]=(char)WriteCommandWord;
	buf[3]=(char)EndMark;
	buf[4]=(char)WriteCommandWord;
	buf[5]=Data;
	buf[6]=(char)0x00;
	buf[7]=(char)EndMark;
	unsigned char ADDR_H = Address/256;
	unsigned char ADDR_L = Address%256;
	buf[1]=ADDR_H;
	buf[2]=ADDR_L;
	
	if(!WriteData(buf))
		return FALSE;
	if(!ReadData(buf))
		return FALSE;
	for (int i = 0; i < 8; i++){
		if(buf[i] != 0xA5)
			return FALSE;
	}
	return TRUE;
}

BOOL CUSBDrive::WriteData(int Address, LPVOID lpBuff)
{
	unsigned char buf[8],buf1[8]="";
	char buf2[32];
	::memcpy( &buf2[0],lpBuff,32);
	buf[0]=(char)WriteCommand;
	buf[3]=(char)EndMark;
	buf[4]=(char)WriteCommand;
	buf[5]=(char)0x00;
	buf[6]=(char)0x00;
	buf[7]=(char)EndMark;
	unsigned char ADDR_H = Address/256;
	unsigned char ADDR_L = Address%256;
	buf[1]=ADDR_H;
	buf[2]=ADDR_L;
		
	if(!WriteData(buf))
		return FALSE;

	::memcpy(buf1,&buf2[0],8);	
	if(!WriteData(buf1))
		return FALSE;
	
	::memcpy(buf1,&buf2[8],8);	
	if(!WriteData(buf1))
		return FALSE;

	::memcpy(buf1,&buf2[16],8);		
	if(!WriteData(buf1))
		return FALSE;

	::memcpy(buf1,&buf2[24],8);	
	if(!WriteData(buf1))
		return FALSE;
	
	if(!ReadData(buf))
		return FALSE;
	for (int i = 0; i < 8; i++){
		if(buf[i] != 0xA5)
			return FALSE;
	}

	return TRUE;
}

BOOL CUSBDrive::ReadData(int Address, LPVOID lpBuff)
{
	char buf[8],buf1[8]="";
	char buf2[32];
	buf[0]=(char)ReadCommand;
	buf[3]=(char)EndMark;
	buf[4]=(char)ReadCommand;
	buf[5]=(char)0x00;
	buf[6]=(char)0x00;
	buf[7]=(char)EndMark;
	unsigned char ADDR_H = Address/256;
	unsigned char ADDR_L = Address%256;
	buf[1]=ADDR_H;
	buf[2]=ADDR_L;
		
	if(!WriteData(buf))
		return FALSE;
	if(!ReadData(buf1))
		return FALSE;
	::memcpy(&buf2[0],buf1,8);
		
	if(!ReadData(buf1))
		return FALSE;
	::memcpy(&buf2[8],buf1,8);
		
	if(!ReadData(buf1))
		return FALSE;
	::memcpy(&buf2[16],buf1,8);
		
	if(!ReadData(buf1))
		return FALSE;
	::memcpy(&buf2[24],buf1,8);
	
	::memcpy(lpBuff,&buf2[0],32);
	
	return TRUE;
}

BOOL CUSBDrive::CheckHandle()
{
	m_HidHandle=FindHandle();

	_HIDD_ATTRIBUTES hidAttributes;
	if(!HidD_GetAttributes(m_HidHandle, &hidAttributes))
		{
		CloseHandle(m_HidHandle);
		return false;
		}
	return true;
}


BOOL CUSBDrive::ReadUSBParameter(unsigned char *Parameter)
{
	return(ReadData(0x00,(LPVOID)Parameter) &&
		   ReadData(0x20,(LPVOID)(Parameter+32)) &&
		   ReadData(0x40,(LPVOID)(Parameter+64)) &&
		   ReadData(0x60,(LPVOID)(Parameter+96)) &&
		   ReadData(0x80,(LPVOID)(Parameter+128)) &&
		   ReadData(0xa0,(LPVOID)(Parameter+160)) &&
		   ReadData(0xc0,(LPVOID)(Parameter+192)) &&
		   ReadData(0xe0,(LPVOID)(Parameter+224)));
}
