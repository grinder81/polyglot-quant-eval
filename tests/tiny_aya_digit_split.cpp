#include "unicode.h"
#include <iostream>
#include <iomanip>

int main() {
    const auto parts = unicode_regex_split("  46", {"\\d{1,3}(?=(?:\\d{3})*\\b)"}, false);
    for (const auto & part : parts) std::cout << std::quoted(part) << '\n';
    return 0;
}
