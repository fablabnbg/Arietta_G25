firefox http://devicetree.org/Device_Tree_Usage

------------------
# configure online


ttyS2 (usart1) TXD is pin 28 (aka PA5) ttyS1 (usart0) TXD is pin 23 (aka 
PA0) SPI MOSI is pin 8 (aka PA22) acme-arietta-dtb acme-arietta-dts 
settings generated with http://dts.acmesystems.it/arietta/ 

ttyS1, ttyS2, ttyS3
SPI /dev/spi0
A/D converter
1wire PC2



-----------------
# compile manually

vi arch/arm/boot/dts/acme-arietta.dts

make ARCH=arm CROSS_COMPILE=arm-linux-gnueabi- acme-arietta.dtb 
VERBOSE=1

-----------------
# install

scp arch/arm/boot/dts/acme-arietta.dtb root@192.168.10.10:/boot

