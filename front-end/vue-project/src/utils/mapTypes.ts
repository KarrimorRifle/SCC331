export interface preset {
  id: string | number,
  name: string,
  trusted: Array<number>,
  boxes: Array<boxType>,
  owner_id: string | number,
  image: {
    name: string,
    data: string,
  },
}

export interface boxType {
  roomID: string,
  label: string,
  top: number,
  left: number,
  width: number,
  height: number,
  colour: string
}

export interface presetListType {
  default: string,
  presets: Array<{
    name: string,
    id: number
  }>
}

export interface image {
  name: string,
  data: string
}

export interface boxAndData {
  [id: string]: dataObject
}

export interface dataObject {
  label: string,
  tracker: environmentData,
  box: {
    top: number,
    left: number,
    width: number,
    height: number,
    colour: string
  } | null
}

export interface environmentData {
    users: countAndID,
    luggage: countAndID,
    environment:{
      temperature: number,
      sound: number,
      light: number,
      IAQ: number,
      pressure: number,
      humidity: number,
    }
  }

export interface summaryType {
  [id: string]: environmentData
}

export interface countAndID {
  count: number,
  id: Array<string>
}