# Epic Coding Standard Fixer

Python script that fixes source code in order to match epic coding standard for unreal engine

Run script.py with python 3.8 and follow prompted instructions

## if-blocks in .cpp files

Example 1
```
    // before
    if (condition) function();

    // after
    if (condition) 
    {
        function();
    }
```

Example 2
```
    // before
    if (conditionA && 
        conditionB && 
        conditionC) 
        function();

    // after
    if (conditionA && 
        conditionB && 
        conditionC)
    {
        function(); 
    }
```

Example 3
```
    // before
    if (conditionA && // a comment
        conditionB || // another comment
        conditionC) // last comment
        function();

    // after
    if (conditionA && // a comment
        conditionB || // another comment
        conditionC) // last comment
    {
        function();
    }
```

Example 4
```
    // before
    if (conditionC)
        if (conditionA)
            if (conditionB)
                function();  

    // after
    if (conditionA)
    {
        if (conditionB)
        {
            if (conditionC)
            {
                function();
            }
        }     
    }
```

## copyright comments in .h and .cpp files

Example 1
```
// Before

// Fill in copyright here

#pragma once

#include "CoreMinimal.h"

...

// After

// Copyright comment, all rights reserved

#pragma once

#include "CoreMinimal.h"

...
```

Example 2
```
// Before

#pragma once

#include "CoreMinimal.h"

...

// After

// Copyright comment, all rights reserved

#pragma once

#include "CoreMinimal.h"

...
```