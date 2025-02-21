export const checkEnvironmentCondition = (roomInfo: any, variable: string, lower_bound: number, upper_bound: number): boolean => {
    /**
     * Checks if an environmental variable in a room falls within the specified bounds.
     */
    if (variable.toLowerCase() in roomInfo?.environment) {
      const value = roomInfo.environment[variable.toLowerCase()];
      return lower_bound <= value && value <= upper_bound;
    }
    return false;
};
  
export const checkLuggageCondition = (roomInfo: any, lower_bound: number, upper_bound: number): boolean => {
    /**
     * Checks if the luggage count in a room falls within the specified bounds.
     */
    if ("luggage" in roomInfo) {
        const value = roomInfo.luggage.count;
        return lower_bound <= value && value <= upper_bound;
    }
    return false;
};
  
export const checkWarningAreas = (roomData: any, warning: any): { roomID: string, messages: any[] }[] => {
    /**
     * Checks which rooms fully meet all warning conditions and retrieves the associated messages.
     */
    const triggeredRooms: Record<string, Set<string>> = {}; // Store unique messages per room

    warning.conditions.forEach((roomCondition: any) => {
        const roomID = roomCondition.roomID;
        if (roomData[roomID]) {
            const roomInfo = roomData[roomID];
            let allConditionsMet = false; 

            roomCondition.conditions.forEach((rule: any) => {
                const { variable, lower_bound, upper_bound } = rule;

                // Check environmental variables
                if (!checkEnvironmentCondition(roomInfo, variable, lower_bound, upper_bound)) {
                    console.log("meet")
                    allConditionsMet = true; 
                }

                // Check luggage count
                if (variable === "Luggage" && !checkLuggageCondition(roomInfo, lower_bound, upper_bound)) {
                    allConditionsMet = true;
                }
            });

            // ✅ If all conditions are met, store messages
            if (allConditionsMet) {
                if (!triggeredRooms[roomID]) {
                    triggeredRooms[roomID] = new Set();
                }

                warning.messages.forEach(msg => {
                    if (msg.Location === roomID) {
                        triggeredRooms[roomID].add(JSON.stringify(msg)); // Store as a unique JSON string
                    }
                });
            }
        }
    });

    // Convert stored messages back to an array of objects
    return Object.entries(triggeredRooms).map(([roomID, messages]) => ({
        roomID,
        messages: Array.from(messages).map(msg => JSON.parse(msg)), // Convert back from JSON strings
    }));
};
