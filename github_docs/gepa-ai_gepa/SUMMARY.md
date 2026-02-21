# Detailed Summary: gepa-ai_gepa

*Auto-generated comprehensive documentation summary*

---

# Comprehensive Documentation Summary for the GEPA Repository

## 1. Project Overview & Purpose

### What is this project and what problem does it solve?
**GEPA** (Genetic-Pareto) is a framework designed to optimize systems composed of text components—such as AI prompts, code snippets, or textual specifications—against any evaluation metric. It utilizes large language models (LLMs) to reflect on system behavior, leveraging feedback from execution and evaluation traces to drive targeted improvements. The core innovation of GEPA is its ability to evolve robust, high-performing variants of text components through iterative mutation, reflection, and Pareto-aware candidate selection, minimizing the number of evaluations needed.

### Target audience and use cases
The primary audience includes AI researchers, developers, and data scientists who are looking to enhance the performance of systems that rely on textual inputs. Use cases span various domains, including:
- AI prompt optimization for chatbots and virtual assistants.
- Code generation and optimization in software development.
- Textual specifications for machine learning models.
- Enhancements in retrieval-augmented generation (RAG) systems.

### Project history, maturity, and current status
GEPA is based on the research paper titled "GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning," which outlines its theoretical foundations and practical applications. The project is actively maintained, with ongoing developments aimed at expanding its capabilities and integrations with various frameworks.

### Key differentiators from similar projects
GEPA stands out due to its evolutionary optimization approach, which combines genetic algorithms with Pareto optimization principles, allowing it to efficiently explore the solution space. Unlike traditional reinforcement learning methods, GEPA minimizes the need for extensive training data and evaluations, making it more efficient for optimizing text-based systems.

## 2. Key Features & Capabilities

### Major Features
1. **Reflective Text Evolution**:
   - **What it does**: Evolves text components through iterative feedback loops.
   - **Why it's useful**: Allows for continuous improvement of prompts and instructions based on real-world performance.
   - **When to use it**: Ideal for applications requiring dynamic adaptation to user interactions or changing contexts.
   - **Limitations**: May require a sufficient initial dataset for effective evolution.

2. **Integration with LLMs**:
   - **What it does**: Interfaces with various LLMs for both task execution and reflection.
   - **Why it's useful**: Leverages state-of-the-art language models to enhance the quality of generated text.
   - **When to use it**: When high-quality language generation is critical for the application.
   - **Limitations**: Dependency on external LLM services may incur costs and require API keys.

3. **Multi-Component Optimization**:
   - **What it does**: Simultaneously optimizes multiple text components within a system.
   - **Why it's useful**: Facilitates holistic improvements across interconnected components, enhancing overall system performance.
   - **When to use it**: In complex systems where multiple text components interact.
   - **Limitations**: Increased complexity in managing interactions between components.

4. **Adapter Architecture**:
   - **What it does**: Provides a flexible interface for integrating GEPA with various systems and frameworks.
   - **Why it's useful**: Enables easy adaptation of GEPA to different environments and use cases.
   - **When to use it**: When integrating GEPA into existing workflows or systems.
   - **Limitations**: Requires development effort to create custom adapters for new systems.

5. **Evaluation Metrics**:
   - **What it does**: Implements comprehensive metrics for assessing both retrieval and generation quality.
   - **Why it's useful**: Provides insights into the effectiveness of optimizations and guides further improvements.
   - **When to use it**: During the optimization process to track progress and effectiveness.
   - **Limitations**: May require domain-specific adjustments to metrics for optimal relevance.

## 3. Architecture & Technical Design

### Overall system architecture with component descriptions
The GEPA framework consists of several core components:
- **GEPA Core**: The main engine that manages the optimization process.
- **Adapters**: Interfaces that allow GEPA to connect with various systems, such as DSPy or custom applications.
- **LLMs**: Large language models used for generating and evaluating text components.
- **Evaluation Metrics**: Tools for assessing the performance of generated outputs.

### Design patterns and principles used
GEPA employs an evolutionary algorithm approach, utilizing principles from genetic algorithms, such as selection, mutation, and crossover, combined with Pareto optimization to balance multiple objectives.

### Data flow and component interactions
1. **Input Data**: The system receives initial text components and evaluation metrics.
2. **Optimization Loop**: GEPA iteratively mutates text components, evaluates their performance using LLMs, and selects the best candidates based on predefined metrics.
3. **Output Generation**: The optimized text components are produced and can be integrated back into the system.

### Technology stack and why each piece was chosen
- **Python**: The primary programming language due to its rich ecosystem for machine learning and data science.
- **LLMs (e.g., OpenAI, Ollama)**: Chosen for their state-of-the-art performance in natural language understanding and generation.
- **Custom Adapters**: Allow for flexibility in integrating with various systems, making GEPA versatile across different applications.

### Scalability and performance considerations
GEPA is designed to scale with the complexity of the systems it optimizes. The use of evolutionary algorithms allows it to efficiently explore large solution spaces without exhaustive evaluations.

## 4. Installation & Setup

### Detailed step-by-step installation for different platforms
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/gepa-ai/gepa
   cd gepa
   ```

2. **Install Dependencies**:
   - Using `pip`:
   ```bash
   pip install gepa
   ```
   - For the latest version from `main`:
   ```bash
   pip install git+https://github.com/gepa-ai/gepa.git
   ```

### All prerequisites with specific version requirements
- **Python**: Version 3.10 or later is required.
- **Dependencies**: Specific libraries will be installed based on the chosen adapter and vector store.

### Configuration file locations and structures
Configuration files are typically located in the `src/gepa/config` directory, where users can define parameters for the optimization process.

### Initial setup and bootstrapping process
After installation, users should set up their environment and any necessary API keys for LLMs. This can be done by exporting environment variables:
```bash
export OPENAI_API_KEY="your-api-key"
```

### Verification steps to confirm successful installation
Run unit tests to verify the installation:
```bash
uv run pytest tests/
```

### Common installation issues and troubleshooting
- **Missing Dependencies**: Ensure all required libraries are installed as per the requirements files.
- **API Key Issues**: Verify that API keys are correctly set and have the necessary permissions.

## 5. Core Components & Modules

### Detailed description of each major component
1. **GEPA Core**: The main engine that orchestrates the optimization process.
2. **Adapters**: Interfaces that allow GEPA to connect with various systems, such as DSPy or custom applications.
3. **LLMs**: Large language models used for generating and evaluating text components.
4. **Evaluation Metrics**: Tools for assessing the performance of generated outputs.

### Purpose and responsibilities of each module
- **GEPA Core**: Manages the optimization loop and integrates with LLMs.
- **Adapters**: Facilitate communication between GEPA and external systems.
- **LLMs**: Generate text and provide feedback for optimization.
- **Evaluation Metrics**: Measure the effectiveness of generated outputs.

### How components interact and depend on each other
The GEPA Core interacts with Adapters to receive input data, communicates with LLMs for text generation and evaluation, and uses Evaluation Metrics to assess performance and guide the optimization process.

### Extension points and customization options
Users can create custom Adapters to integrate GEPA with their systems, allowing for tailored optimization processes.

### Internal APIs and interfaces
The internal APIs are defined in the `src/gepa/core` directory, where users can find interfaces for creating Adapters and interacting with the GEPA Core.

## 6. Usage Guide & Examples

### Basic usage with simple examples
To optimize a prompt using GEPA:
```python
import gepa

# Define the initial prompt
seed_prompt = {
    "system_prompt": "You are a helpful assistant."
}

# Run optimization
result = gepa.optimize(
    seed_candidate=seed_prompt,
    trainset=train_data,
    valset=val_data,
    task_lm="openai/gpt-4.1-mini",
    max_metric_calls=150
)

print("Optimized Prompt:", result.best_candidate['system_prompt'])
```

### Advanced usage patterns with detailed examples
For optimizing a multi-turn agent:
```python
# Define a custom adapter for a multi-turn agent
class CustomAdapter(gepa.GEPAAdapter):
    def evaluate(self, candidate, inputs):
        # Custom evaluation logic
        pass

# Run optimization with the custom adapter
result = gepa.optimize(
    seed_candidate=seed_prompt,
    trainset=train_data,
    valset=val_data,
    adapter=CustomAdapter(),
    max_metric_calls=200
)
```

### Common workflows and how to accomplish them
1. **Prompt Optimization**: Use the `optimize` function with a seed prompt and training data.
2. **Program Evolution**: Implement a custom adapter to evolve entire programs, not just prompts.

### Best practices and recommended approaches
- Start with a well-defined seed prompt.
- Use sufficient training data to guide the optimization process.
- Regularly evaluate and adjust parameters based on performance metrics.

### Real-world use case examples
1. **Chatbot Optimization**: Using GEPA to refine prompts for a customer service chatbot, resulting in improved user satisfaction scores.
2. **Code Generation**: Optimizing code snippets for a programming assistant, leading to higher accuracy in generated code.

### Code snippets demonstrating key features
```python
# Example of using GEPA with a custom adapter
result = gepa.optimize(
    seed_candidate={"prompt": "What is the capital of France?"},
    trainset=train_data,
    valset=val_data,
    adapter=CustomAdapter(),
    max_metric_calls=100
)
```

## 7. API / CLI Reference

### Complete list of available APIs, endpoints, or commands
- **`gepa.optimize`**: Main function for running the optimization process.
- **`GEPAAdapter`**: Base class for creating custom adapters.

### For each API/command:
- **Purpose and description**: Optimizes text components using evolutionary algorithms.
- **Parameters and their meanings**:
  - `seed_candidate`: Initial text component to optimize.
  - `trainset`: Dataset used for training the optimization process.
  - `valset`: Dataset used for validation.
  - `adapter`: Custom adapter for integrating with external systems.
  - `max_metric_calls`: Maximum number of evaluations to perform.
- **Return values and response formats**: Returns an object containing the best candidate and evaluation metrics.
- **Usage examples**:
```python
result = gepa.optimize(seed_candidate=seed_prompt, trainset=train_data, valset=val_data)
```
- **Error codes and handling**: Common errors include missing dependencies and invalid API keys.

## 8. Configuration & Customization

### All configuration options with descriptions
- **`seed_candidate`**: The initial text component to optimize.
- **`trainset`**: The dataset used for training the optimization process.
- **`valset`**: The dataset used for validation.
- **`adapter`**: The custom adapter for integrating with external systems.
- **`max_metric_calls`**: The maximum number of evaluations to perform.

### Default values and recommended settings
- Default values are generally set to reasonable defaults, but users are encouraged to customize based on their specific use cases.

### Environment variables and their effects
- **`OPENAI_API_KEY`**: Required for using OpenAI's models.
- **`ANTHROPIC_API_KEY`**: Required for using Anthropic's models.

### Configuration file formats and examples
Configuration files are typically in JSON or YAML format, allowing for easy editing and integration.

### Advanced configuration scenarios
Users can define complex configurations for multi-component systems by creating custom adapters that implement the `GEPAAdapter` interface.

### Performance tuning options
- Adjusting `max_metric_calls` to optimize for speed vs. thoroughness.
- Fine-tuning the `adapter` to better suit specific system requirements.

## 9. Dependencies & Requirements

### Complete list of dependencies with versions
- **litellm**: `>=1.64.0`
- **chromadb**: `>=0.4.0`
- **weaviate-client**: `>=4.0.0`
- **qdrant-client**: `>=1.15.0`
- **pymilvus**: `>=2.6.0`
- **lancedb**: `>=0.22.0`
- **pyarrow**: `>=10.0.0`

### System requirements (OS, hardware, etc.)
- **OS**: Compatible with Linux, macOS, and Windows.
- **Hardware**: Recommended to have at least 8GB of RAM for optimal performance.

### Optional dependencies and what they enable
- Additional libraries for specific vector stores or advanced features.

### Dependency installation and management
Dependencies can be installed using `pip` and are listed in the `requirements-rag.txt` file.

### Compatibility matrix
A matrix detailing compatibility with various vector stores and LLMs is available in the documentation.

## 10. Development & Contributing

### How to set up development environment
1. **Fork the repository** and clone it locally.
2. **Set up a Python environment** using `uv` or `conda`.
3. **Install development dependencies** as specified in the `requirements.txt`.

### Build process and tooling
Use standard Python build tools and follow the structure laid out in the repository.

### Testing approach and running tests
Run unit tests using `pytest` to ensure code quality and functionality.

### Code structure and organization
The code is organized into modules, with clear separation between core functionality, adapters, and examples.

### Contributing guidelines
Contributions are welcome! Please refer to the `CONTRIBUTING.md` file for detailed instructions on how to contribute.

### Release process
Releases are managed through GitHub, with versioning based on semantic versioning principles.

## 11. Deployment & Production

### Production deployment strategies
- Use containerization (e.g., Docker) for deploying GEPA in production environments.
- Consider using cloud-based LLMs for scalability.

### Scaling considerations
- Monitor resource usage and optimize configurations based on load.
- Use caching strategies for frequently accessed data.

### Monitoring and observability
Implement logging and monitoring to track performance and identify issues.

### Backup and disaster recovery
Regularly back up configurations and data to prevent loss.

### Security best practices
- Secure API keys and sensitive data.
- Implement access controls for production environments.

### Performance optimization
Regularly review and optimize configurations based on performance metrics.

## 12. Troubleshooting & Common Issues

### Known issues and limitations
- Dependency conflicts may arise; ensure all required libraries are installed.
- API rate limits may affect performance when using cloud-based LLMs.

### Common error messages and solutions
- **Missing API Key**: Ensure the `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` is set correctly.
- **Import Errors**: Verify that all dependencies are installed.

### Debugging techniques and tools
Use logging and debugging tools to trace issues during development.

### Where to get help
- **GitHub Issues**: Open an issue for specific questions or problems.
- **Community Forums**: Engage with the community for support and discussions.

### FAQ items
- **How do I contribute to GEPA?**: Refer to the `CONTRIBUTING.md` file for guidelines.
- **Can I use GEPA with my own LLM?**: Yes, by implementing a custom adapter.

## 13. Additional Resources

### Links to tutorials and guides
- [DSPy GEPA Tutorials](https://dspy.ai/tutorials/gepa_ai_program/): Step-by-step guides for using GEPA with DSPy.

### Community resources
- **Discord Channel**: Join the community for discussions and support.

### Related projects and integrations
- **DSPy**: Integration with DSPy for optimizing program signatures.

### Changelog highlights
Refer to the `CHANGELOG.md` for detailed updates and changes in each version.

---

This comprehensive summary provides a detailed overview of the GEPA repository, covering all essential aspects, including project purpose, features, architecture, installation, usage, API references, configuration, dependencies, development, deployment, troubleshooting, and additional resources.