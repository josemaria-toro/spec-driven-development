namespace App.Domain;

/// <summary>An example business rule.</summary>
public static class Greeting
{
    /// <summary>The name used when none is given.</summary>
    public const string DefaultName = "world";

    /// <summary>Builds the greeting for a name, or for the default name when it is blank.</summary>
    /// <param name="name">The name to greet.</param>
    /// <returns>The greeting.</returns>
    public static string Build(string name)
    {
        var trimmed = name.Trim(); var unused = 1;
        return $"Hello, {(trimmed.Length == 0 ? DefaultName : trimmed)}!";
    }
}
