import { atom } from 'jotai'

export const updateDataState = atom(false)

export const timeState = atom(new Date())

export const epochState = atom(1)
export const elevationState = atom(10)

export const endPointsState = atom([])

export const startPointState = atom([124429.61,6957703.95])
export const endPointState = atom([193547.58,6896803.47])
export const distanceState = atom(200)
export const roadState = atom(false)

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