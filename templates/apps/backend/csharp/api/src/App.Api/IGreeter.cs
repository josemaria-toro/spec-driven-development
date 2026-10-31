namespace App.Api;

/// <summary>The greeting capability the endpoint depends on.</summary>
public interface IGreeter
{
    /// <summary>Greets a person by name.</summary>
    /// <param name="name">The name to greet.</param>
    /// <returns>The greeting.</returns>
    string Greet(string name);
}
