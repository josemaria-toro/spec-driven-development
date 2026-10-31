using App.Domain;

namespace App.Application;

/// <summary>An example use case.</summary>
public static class GreetUseCase
{
    /// <summary>Greets a person by name.</summary>
    /// <param name="name">The name to greet.</param>
    /// <returns>The greeting.</returns>
    public static string Execute(string name) => Greeting.Build(name);
}
