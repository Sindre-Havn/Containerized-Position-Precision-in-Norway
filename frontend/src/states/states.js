import { atom } from 'jotai'

export const updateDataState = atom(false)

export const timeState = atom(new Date())

export const epochState = atom(1)
export const epochFrequencyState = atom(30)
export const elevationState = atom(10)

export const endPointsState = atom([])

export const vegReferanseState = atom('EV136')
export const startPointState = atom([124657.85,	6957624.16])
export const endPointState = atom([193510.27,6896504.01])
export const distanceState = atom(1000)

export const roadState = atom(false)

export const pointsState = atom([])

export const geoJsonDataState = atom(null)

export const updateDOPState = atom(false)

export const chosenPointState = atom(0)

export const gnssState = atom({
    GPS: true,
    GLONASS: true,
    Galileo: true,
    BeiDou: true,
    QZSS: true,
    NavIC: false,
  
  })

export const gnssState2 = atom({
    GPS: true,
    GLONASS: true,
    Galileo: true,
    BeiDou: true,
    QZSS: true,
    NavIC: false,

  })
export const roadProgressState = atom(0)