def olci_vicarious(vicar_version):

    #null
    if vicar_version == 'olci_null':
        vicar_gains = {
            400: 1.000000, 412: 1.000000,
            443: 1.000000, 490: 1.000000,
            510: 1.000000, 560: 1.000000,
            620: 1.000000, 665: 1.000000,
            674: 1.000000, 681: 1.000000,
            709: 1.000000, 754: 1.000000,
            760: 1.000000, 764: 1.000000,
            767: 1.000000, 779: 1.000000,
            865: 1.000000, 885: 1.000000,
            900: 1.000000, 940: 1.000000,
            1020: 1.000000,
        }
        return vicar_gains

    #SVC 01/08/19
    elif vicar_version == 'olci_scv2019':
        vicar_gains = {
            400: 1.000000, 412: 1.000000,
            443: 0.999210, 490: 0.984674,
            510: 0.986406, 560: 0.988970,
            620: 0.991810, 665: 0.987590,
            674: 1.000000, 681: 1.000000,
            709: 1.000000, 754: 1.000000,
            760: 1.000000, 764: 1.000000,
            767: 1.000000, 779: 1.000000,
            865: 1.000000, 885: 1.000000,
            900: 1.000000, 940: 1.000000,
            1020: 1.000000,
        }
        return vicar_gains

    else:
        print('Recalibration gains ' + vicar_version + ' not found.')
        raise RuntimeError("Polymer recalibration failed.")


def msi_vicarious(vicar_version):

    #null
    if vicar_version == 'msi_null':
        vicar_gains = {
            443: 1.000000, 490: 1.000000,
            560: 1.000000, 665: 1.000000,
            705: 1.000000, 740: 1.000000,
            783: 1.000000, 842: 1.000000,
            865: 1.000000, 945: 1.000000,
            1375: 1.000000, 1610: 1.000000,
            2190: 1.000000,
        }
        return vicar_gains

    else:
        print('Recalibration gains ' + vicar_version + ' not found.')
        raise RuntimeError("Polymer recalibration failed.")