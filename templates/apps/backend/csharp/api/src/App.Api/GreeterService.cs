using App.Application;

namespace App.Api;

/// <summary>Greets through the application use case.</summary>
public sealed class GreeterService : IGreeter
{
    /// <inheritdoc />
    public string Greet(string name) => GreetUseCase.Execute(name);
}
